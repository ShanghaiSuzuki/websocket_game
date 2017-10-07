//とりあえずブラウザ画面への出力用
function print(message){
    var messages = $("#text_box").val();
	$("#text_box").val(message + "\n" + messages);
}

//HexとCanvasを管理するクラス
//ヘックスの一辺の長さとフィールドの広さからヘックスグリッドを定義する
function HexGrid(socket) {

	print("HexGrid: in constructor : ver 0.11");

	//canvasとコンテキストを初期化
	this.canvas = document.getElementById("field");
	this.context = this.canvas.getContext("2d");

	this.canvas.width = $("#field").width();
	this.canvas.height = $("#field").height();

	//canvas上のプレイヤー
	this.players = {};

	//自身の情報
	this._self_info = [];

    //描写設定
    this._fps = 1000/30; //30fps
    this._last_time_rendered = 0;

	//辺の長さ
	this.length = undefined;

	//ヘックス描写に使う数値を事前計算
	this.half_len = undefined;
	this.delta_v = undefined;

	//フィールドの広さ
	this.width = undefined;
	this.height = undefined;

	//Hexの集合
	this.hexagons = null;

	//標準空間とグリッド空間の座標変換
	this.matNormToGrid = null;
	this.matGridToNorm = null;

	//標準空間と格納空間の座標変換
	this.matNormToIndex = null;
	this.matIndexToNorm = null;

	//描写領域の座標変換の初期設定と制限範囲
	this.scale = 1;
	this.zoom_max = 2;
	this.zoom_min = 0.5;
	this.translate = [0, 0];
	//this.translate_min = [-width + this.canvas.width, -height + this.canvas.height];
	this.translate_min = undefined
	this.translate_max = [0, 0];

	//イベントハンドラ内のパラメータの初期値
	this.dragging = false;
	this._ex_up_time= 0.0;

	//ソケット
	this.socket = socket;

	//initはwebsocketのハンドラとして起動する
	this.socket.bindHandler("init_hexgrid", this.init.bind(this));

	//更新用のハンドラ
    this.socket.bindHandler("update_hexgrid", this.update.bind(this));

    //サーバにリクエストを送信し初期化開始
	this.socket.send("init_hexgrid", {});

}

//初期化:ヘックスグリッド作成
HexGrid.prototype.init = function(data) {

    //フィールドを定義する三つの変数
	this.width = data["width"];
	this.height = data["height"];
	this.length = data["length"];

	//Hex描写に使う変数
	this.half_len = this.length / 2;
	this.delta_v = this.length * Math.sin(1 / 3 * Math.PI);

	//平行移動の制限
	this.translate_min = [-this.width + this.canvas.width, -this.height + this.canvas.height];

	//ヘックスのオフセットと増分
	var x_offset = this.length;
	var y_offset = this.length * Math.sin(1 / 3 * Math.PI);
	var delta_x = 3 / 2 * this.length;
	var delta_y = y_offset;

	//アフィン変換行列
	this.matGridToNorm= math.matrix(
		[
			[delta_x, 0, x_offset],
			[-(delta_y), 2 * delta_y, y_offset],
			[0, 0, 1]
		]);

	this.matNormToGrid= math.inv(this.matGridToNorm);

	this.matIndexToNorm = math.matrix(
		[
			[this.length * 3 / 2, 0, this.length],
			[0, delta_y * 2, delta_y],
			[0, 0, 1]
		]);

	this.matNormToIndex = math.inv(this.matIndexToNorm);

	//ヘックスグリッドの配列確保
	var num_hex_w = this.width - x_offset;
	num_hex_w = Math.floor(num_hex_w / delta_x);
	var num_hex_h = this.height - y_offset;
	num_hex_h = Math.floor(num_hex_h / delta_y / 2);
	this.hexagons = new Array(num_hex_w);
	for (var i = 0; i < num_hex_w; i++) {
		this.hexagons[i] = new Array(num_hex_h);
	}

	//グリッド生成
	var x = x_offset;
	var col = 0;
	var n = 0;
	while ((x + delta_x + (this.length / 2)) < this.width) {
		var y = y_offset;
		if (col % 2 == 1) {
			y += delta_y;
		}

		while ((y + delta_y * 3) < this.height) {

			//グリッド空間の座標に変換
			var g_vec = math.multiply(this.matNormToGrid, [x, y, 1]);
			var g_col = math.round(g_vec.valueOf()[0]);
			var g_row = math.round(g_vec.valueOf()[1]);

			//格納空間の座標に変換
			var i_vec = math.multiply(this.matNormToIndex, [x, y, 1]);
			var i_col = math.round(i_vec.valueOf()[0]);
			var i_row = math.round(i_vec.valueOf()[1]);

			var hex = new Hex([g_col, g_row], x, y);
			this.hexagons[i_col][i_row] = hex;
			y += delta_y * 2;
		}

		x += delta_x;
		col++;

	}

	//イベントリスナーでキャッチするイベントを登録
	//TODO: スマホ版とPC版でクラス分けする？
	this.canvas.addEventListener("mousewheel", this, false);
	this.canvas.addEventListener("mousedown", this, false);
	this.canvas.addEventListener("mouseup", this, false);
	this.canvas.addEventListener("mousemove", this, false);
	this.canvas.addEventListener("mouseleave", this, false);
	this.canvas.addEventListener("touchstart", this, false);
	this.canvas.addEventListener("touchend", this, false);
	this.canvas.addEventListener("touchmove", this, false);

	//ハンドラ初期設定は通常のイベントハンドラで、メニュー等からフックされる
    this.handleEvent = this.normal_event_handler;

    //自身の情報を設定
    this._self_info["name"] = data["name"];
    this._self_info["col"] = data["col"];
    this._self_info["row"] = data["row"];
    this._self_info["country"] = data["country"];

    //描写情報更新
    this.update(data);

    print("HexGrid初期化完了");
    this.render();
}

//ヘックスグリッドが更新された時のハンドラ
HexGrid.prototype.update = function(data){

    print("in HexGrid.update");
    //可視になった領域を読み込み
    for(var i=0; i<data["visible_area"].length; i++){
        var index = this._gridToIndex([data["visible_area"][i][0], data["visible_area"][i][1]]);
        this.hexagons[index[0]][index[1]].change_type(data["visible_area"][i][2]);
        this.hexagons[index[0]][index[1]].set_status(true);
    }

    //不可視になった領域を読み込み
    for(var i=0; i<data["unvisible_area"].length; i++){
        print("in update unvisible_area col");
        var index = this._gridToIndex([data["unvisible_area"][i][0], data["unvisible_area"][i][1]]);
        this.hexagons[index[0]][index[1]].change_type(data["unvisible_area"][i][2]);
        this.hexagons[index[0]][index[1]].set_status(false);
    }

    // 新しく現れたプレイヤーを読み込み
    for(var i=0; i<data["new_players"].length; i++){
        var name = data["new_players"][i][0];
        this.players[name] = {}
        this.players[name]["name"] = name;
        this.players[name]["index"] = this._gridToIndex([data["players"][i][1], data["players"][i][2]]);
        this.players[name]["country"] = data["players"][i][4];
        this.players[name]["icon"] = new Image();
        this.players[name]["icon"].src = "static/resource/icon/" + data["players"][i][3] +".jpeg";
        this.hexagons[this.players[name]["index"][0]][this.players[name]["index"][1]].add_player(name, this.players[name]);

        //プレイヤーが自分自身だった場合情報を更新
        if (name == this._self_info["name"]){
            this._self_info["col"] = data["players"][i][0];
            this._self_info["row"] = data["players"][i][1];
        }
    }

    // 不可視になったプレイヤーを読み込み、削除
    for(var i=0; i<data["removed_players"].length; i++){
        name = data["removed_players"][i][0]
        col = data["removed_players"][i][1];
        row = data["removed_players"][i][2];
        this.hexagons[col][row].remove_player(name);
    }

}

//マウス・タッチイベントハンドラ
HexGrid.prototype.normal_event_handler = function(e) {

	//デフォルトのイベントハンドラを停止
	e.preventDefault();
	e.stopPropagation();

	switch (e.type) {

	  case ("mousewheel"):
		 this._is_mouse_down = false;
		 this._scaling(e);
		 this.render();
		 break;

	  case ("mousedown"):
		 this._onMouseDown(e);
		 break;

	  case ("mouseup"):
		this._onMouseUp(e);
		break;

	  case ("mouseleave"):
		this._is_mouse_down = false;
		break;

	  case ("mousemove"):
		this._onMouseMove(e);
		this.render();
		break;

	  case ("touchstart"):
	    this._onTouchStart(e);
	    break;

	  case ("touchmove"):
	    this._onTouchMove(e);
	    this.render();
	    break;

	  case("touchend"):
	    this._onTouchEnd(e);
	    break;

	}

}

HexGrid.prototype._onMouseDown= function(e) {

    this._is_mouse_down = true;

    this._mouse_down_pos = [e.clientX, e.clientY];
}

HexGrid.prototype._onMouseUp = function(e){

    this._is_mouse_down = false;

    //onMouseMoveで使われる移動前の座標の再初期化
    this.ex_pos = undefined;

    //マウスアップ時の時刻
    var up_time = new Date().getTime();

    //ダブルクリック判定
    if((up_time - this._ex_up_time) < 300){
        clearTimeout(this._timer_single_click);
        this._onDoubleClick(e);
        return;
    }
    this._ex_up_time = up_time;

    //シングルクリック判定
    //setTimeoutでダブルクリック判定を待つ
    this._timer_single_click = setTimeout(function(e){
        var x = this._mouse_down_pos[0] - e.clientX;
        var y = this._mouse_down_pos[1] - e.clientY;
        x = x * x;
        y = y * y;
        //mouse downとup時の距離がヘックスの一辺より短ければシングルクリック
        //計算量削減のため距離の計算はルートを取らず、一辺の長さを二乗して行う
        if(this.length * this.length > (x + y)){
            hex_grid_menu.toggle_menu();
        }
        }.bind(this, e), 300);
}

HexGrid.prototype._onMouseMove= function(e) {

	if(this._is_mouse_down !== true) return;

	//移動中の点
	var rect = e.target.getBoundingClientRect();
	var x = e.clientX - rect.left;
	var y = e.clientY - rect.top;
	//var moving_pos = [x / this.scale , y / this.scale];
	var moving_pos = [x  , y  ];


	//移動する前との増分
	var d_pos = this.ex_pos?
		math.subtract(moving_pos, this.ex_pos):
		[0, 0];
	this.ex_pos = moving_pos;

	//canvasの始点を平行移動
	this.translate = math.add(this.translate, d_pos);

	//範囲制限
	this.translate[0] = Math.min(this.translate_max[0], this.translate[0]);
	this.translate[1] = Math.min(this.translate_max[1], this.translate[1]);
	this.translate[0] = Math.max(this.translate_min[0], this.translate[0]);
	this.translate[1] = Math.max(this.translate_min[1], this.translate[1]);
}

HexGrid.prototype._onTouchStart = function(e){

    //マルチタッチ
    if(e.targetTouches.length > 1){
        this._is_multitouch = true;

        //マルチタッチ感の距離を保存（ズーム用）
        var x = e.targetTouches[0].clientX - e.targetTouches[1].clientX;
        var y = e.targetTouches[0].clientY - e.targetTouches[1].clientY;
        // root(x^2 + y^2)は重い処理なので簡略化する
        x = x < 0 ? -x : x;
        y = y < 0 ? -y : y;
        this._ex_touches_length = x + y;

        this._touch_pos = undefined
        return;
    }

    //シングルタッチ
    this._is_multitouch = false;
    this.ex_pos = undefined
    this._touch_pos = [e.targetTouches[0].clientX, e.targetTouches[0].clientY]

}

HexGrid.prototype._onTouchMove = function(e){

    //マルチタッチ中
    if(this._is_multitouch == true){

        //前回のマルチタッチと今回のマルチタッチで距離を計算する
        var x = e.targetTouches[0].clientX - e.targetTouches[1].clientX;
        var y = e.targetTouches[0].clientY - e.targetTouches[1].clientY;
        // root(x^2 + y^2)は重い処理なので簡略化する
        x = x < 0 ? -x : x;
        y = y < 0 ? -y : y;
        var touches_length = x + y;
        this.scale = touches_length / this._ex_touches_length;
        this.scale = Math.min(this.scale, this.zoom_max);
	    this.scale = Math.max(this.scale, this.zoom_min);

    }
    //シングルタッチ中 : 平行移動
    else{

	    //移動中の点
	    var rect = e.target.getBoundingClientRect();
        var x = e.targetTouches[0].clientX - rect.left;
        var y = e.targetTouches[0].clientY - rect.top;
        var moving_pos = [x / this.scale , y / this.scale];


        //移動する前との増分
        var d_pos = this.ex_pos?
            math.subtract(moving_pos, this.ex_pos):
            [0, 0];
        this.ex_pos = moving_pos;

        print("d_pos = " + d_pos);

        //canvasの始点を平行移動
        this.translate = math.add(this.translate, d_pos);

        //範囲制限
        this.translate[0] = Math.min(this.translate_max[0], this.translate[0]);
        this.translate[1] = Math.min(this.translate_max[1], this.translate[1]);
        this.translate[0] = Math.max(this.translate_min[0], this.translate[0]);
        this.translate[1] = Math.max(this.translate_min[1], this.translate[1]);
    }
}

HexGrid.prototype._onTouchEnd = function(e){

    //マルチタッチ判定
    if(this._is_multitouch == true){
        return;
    }


    //ダブルタッチ判定
    var up_time = new Date().getTime(); //タッチエンド時の時刻
    if((up_time - this._ex_up_time) < 300 ){
        clearTimeout(this._timer_single_touch);

        //マウスイベント用のダブルクリック関数を呼ぶ
        e.clientX = e.changedTouches[0].clientX;
        e.clientY = e.changedTouches[0].clientY;
        this._onDoubleClick(e);
        return;
    }
    this._ex_up_time = up_time;

    //シングルクタッチ判定
    //setTimeoutでダブルタッチ判定を待つ
    this._timer_single_touch= setTimeout(function(e){
        var x = this._touch_pos[0] - e.changedTouches[0].clientX;
        var y = this._touch_pos[1] - e.changedTouches[0].clientY;
        x = x < 0 ? -x : x;
        y = y < 0 ? -y : y;
        //mouse downとup時の距離がヘックスの一辺(と係数)より短ければシングルクリック
        //計算量削減のため距離の計算はルートを取らない
        if(this.length * 0.5 > (x + y)){
            hex_grid_menu.toggle_menu();
        }
        }.bind(this, e), 300);

}

//dbclickが上手く発火しないのでmousedownでハンドリングして呼び出す
//touch/mouse共用
HexGrid.prototype._onDoubleClick = function(e){

  //Client座標を標準座標に
  var norm_pos = this._clientToNorm(e);
  norm_pos = [norm_pos[0], norm_pos[1], 1];

  //標準座標からクリックされたヘックスの格納空間の座標を計算する
  var index = this._normToIndex(norm_pos);
  var hex = this.hexagons[index[0]][index[1]];

  HexGridMessage.open("test", "empty");



}

//TODO: スケーリング後に平行移動の制限範囲まで平行移動すると描写領域に何も映らなくなる
//スケーリング後に制限範囲も変更する
HexGrid.prototype._scaling = function(e) {

	//マウスホイール増分
	var d_wheel = e.wheelDelta / 360;
	this.scale += d_wheel;
	this.scale = Math.min(this.scale, this.zoom_max);
	this.scale = Math.max(this.scale, this.zoom_min);
	this.translate_min = [-this.width + this.canvas.width / this.scale,
	                       -this.height + this.canvas.height / this.scale];
	print("scale, width, height : " + this.scale + "," + this.translate_min[0]+ "," + this.translate_min[0]);

}

//Client座標を標準空間に座標変換して取得
HexGrid.prototype._clientToNorm = function(e){

  var rect = e.target.getBoundingClientRect();
  var x = (e.clientX - rect.left) / this.scale;
  x -= this.translate[0];
  var y = (e.clientY - rect.top) / this.scale;
  y -= this.translate[1];
  return [x,y];

}

//標準空間の座標を格納空間のインデックスへ
HexGrid.prototype._normToIndex = function(norm_pos){

  //norm_posがmath.jsのオブジェクト(matrix)の場合識別
  var index_pos = norm_pos.valueOf ?
	[norm_pos.valueOf()[0], norm_pos.valueOf()[1], 1]:
	[norm_pos[0], norm_pos[1], 1];


  index_pos = math.multiply(this.matNormToIndex, index_pos);
  var index = [0,0];
  index[0] = math.round(index_pos.valueOf()[0]);
  index[1] = index[0] % 2 === 0 ?
			 math.round(index_pos.valueOf()[1]):
			 math.ceil(index_pos.valueOf()[1]);

  return index;

}

//グリッド空間のインデックスから格納空間のインデックスへ
HexGrid.prototype._gridToIndex = function(hex_pos){

    //アフィン変換用に整形
    //hex_posがmath.jsのオブジェクト(matrix)の場合識別
    var hex_pos = hex_pos.valueOf ?
	    [hex_pos.valueOf()[0], hex_pos.valueOf()[1], 1]:
	    [hex_pos[0], hex_pos[1], 1];

    //グリッド空間から標準空間へ
    var norm_pos= math.multiply(this.matGridToNorm, hex_pos);

    //標準空間から格納空間へ
    return this._normToIndex(norm_pos);

}

//Client座標からグリッド座標を計算する
HexGrid.prototype.getGridFromEvent = function(e){

    //Client座標を標準座標に
    var norm_pos = this._clientToNorm(e);
    norm_pos = [norm_pos[0], norm_pos[1], 1];

    //標準座標をグリッド座標に
    var g_vec =  math.multiply(this.matNormToGrid, norm_pos);
    var g_col = math.round(g_vec.valueOf()[0]);
    var g_row = math.round(g_vec.valueOf()[1]);
    return [g_col, g_row];

}

//描写
//TODO:指定範囲だけ描写できるようにする
HexGrid.prototype.render = function(start_index, end_index) {

    //30fps
    var now = new Date().getTime();
    if( (now - this._last_time_rendered) < this._fps){
        clearTimeout(this._render_timer);
    }

    this._render_timer  = setTimeout(function(){
        //再描写
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.context.save();
        this.context.scale(this.scale, this.scale);
        this.context.translate(this.translate[0], this.translate[1]);

        for (var i = 0; i < this.hexagons.length; i++) {
            for (var j = 0; j < this.hexagons[i].length; j++) {
                if (this.hexagons[i][j] !== undefined) {
                    this.hexagons[i][j].render(this.context, this.half_len, this.delta_v, true);
                }
            }
        }

        this.context.restore();

        //描写した時刻更新
        this._last_time_rendered = new Date().getTime();
	}.bind(this), this._fps);
}
