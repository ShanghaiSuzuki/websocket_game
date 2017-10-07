/*
HexGridから分離されたメニュー機能
メニュー処理の流れ(例として処理するメニューはmoveとする):

    init内:
        ボタンクリックと_move_front()をバインドする
        サーバからの応答を処理する_move_handlerを、socketにmove(メニュー名)でバインドする

     _move_front:
        サーバに_move_requestイベントを送信して終了
        そのあとの処理は全てサーバと_move_handlerの通信で行う
        (必要があれば処理間で受け渡す必要がある変数などもここで初期化)

     _move_handler:
        サーバはメニュー処理中、
        {event : move, data : { response : foo , bar : bazz, ...}
        このようなメッセージを送信してくる
        _move_handlerはdata["response"]に従って処理を分ける

*/

function HexGridMenu(){

	this._toggle_menu_flag = false;

}

HexGridMenu.prototype.init = function(){


	$("#orbit").css({"z-index":2});

	//初期化時に不可視
	this.toggle_menu();

    //戦争:進軍
	$("#move").bind("click", {}, this._move_front.bind(this));
	hex_grid.socket.bindHandler("move", this._move_handler.bind(this));
}

//メニューを可視/不可視状態にする
HexGridMenu.prototype.toggle_menu= function(visibility){

	if(this._toggle_menu_flag || visibility){
		$("#orbit").css({"visibility":"visible"});
	}
	else{
		$("#orbit").css({"visibility":"hidden"});
	}

	this._toggle_menu_flag = !this._toggle_menu_flag;

}

//メニュー : 戦争.進軍
HexGridMenu.prototype._move_front= function(){

	this.toggle_menu(false);

    //初期化
    this._movables = [];
	//サーバーにmove可能先を問い合わせ

	HexGridMessage.open("進軍選択", "進軍先を選択しますか？", function(){
	    hex_grid.socket.send("move_query", "");
	});

}

HexGridMenu.prototype._move_handler = function(message){

    //サーバより、進軍可能なヘックスを受け取る
    if(message["response"] == "move_query_accept"){

        print("enter move_query_accept")
        //進軍可能なヘックスをライトアップ
        for(var i=0; i<message["movables"].length; i++){

            //グリッド空間から格納空間へ
            var g_vec = [message["movables"][i]["col"], message["movables"][i]["row"]]
            var index = hex_grid._gridToIndex(g_vec);

            //ライトアップ
            hex_grid.hexagons[index[0]][index[1]].set_color("movable", [0, 255,255, 0.2]);

            //所要時間をnotionとして表示
            hex_grid.hexagons[index[0]][index[1]].set_notion(message["movables"][i]["time"]);

            //ライトアップしたヘックスは処理後に戻すため保存
            this._movables.push(index)

        }

        //ライトアップ反映
        hex_grid.render();

        //プレイヤーに進軍先を選択させるため、マウス/タッチイベントハンドラをフック
        hex_grid.handleEvent = function(e){

	        e.preventDefault();
	        e.stopPropagation();

            //touchendかmouseupが呼ばれない場合はフックを解除せずリターン
	        switch(e.type){

	            case("mouseup"):
	                break;

	            case("touchend"):
	                e.clientX = e.changedTouches[0].clientX;
	                e.clientY = e.changedTouches[0].clientY;
	                break;

	            default:
	                return;
	         }

	         //フック解除
	         hex_grid.handleEvent = hex_grid.normal_event_handler;

	         //ライトアップとNOTION解除
	         for(var i=0; i < this._movables.length; i++){
	            hex_grid.hexagons[this._movables[i][0]][this._movables[i][1]].remove_color("movable");
	            hex_grid.hexagons[this._movables[i][0]][this._movables[i][1]].remove_notion();
	         }

	         //反映
	         hex_grid.render();

	         //グリッド座標に変換
	         var grid = hex_grid.getGridFromEvent(e);

	         //確認ポップアップのハンドラ
	         var confirm_handler = function(col, row){

                print("in confirm_handler:サーバーにmove_requestを送信する手前")
                print("col, row = " + col + "," + row);

	            //サーバーに進軍を要請
	            hex_grid.socket.send("move_request", {destination : [col, row]});

	         }.bind(this, grid[0], grid[1]);

	         //確認ポップアップ表示
	         HexGridMessage.open("確認", grid[0] + ", " + grid[1] + "に進軍しますか？<br>" +
	                             "消費食糧 : " + message["food"] + "<br>" +
	                             "消費資金 : " + message["money"],
	                             confirm_handler);

        }.bind(this);

    }

    //進軍可能地域の問い合わせを拒否された
    else if(message["response"] == "deny"){
        HexGridMessage.open("進軍できません", "理由：" + message["reason"]);
    }

    //進軍コマンドが受諾された
    else if(message["response"] == "approval"){
        HexGridMessage.open("進軍中", "到着予定時刻 : " + message["arrival_time"]);
    }
}

//メニュー : 内政.農業
HexGridMenu.prototype._agriculture_front = function(){

	this.toggle_menu(false);

	hex_grid.socket.send("agriculture_query", "")
}

HexGridMenu.prototype._agriculture_handler = function(message){
}

//メニュー : 内政.商業

//メニュー : 内政.徴兵
