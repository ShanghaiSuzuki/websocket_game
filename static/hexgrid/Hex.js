//六角形のクラス
function Hex(hex_id, pos_x, pos_y) {

	//グリッド空間の座標
	this._hex_id = hex_id;

	//標準空間での中心座標
	this._pos_x = pos_x;
	this._pos_y = pos_y;

    //最優先で表示される文字
    this._notion = undefined;

    //地形
    this._type = "UNKNOWN";

    //不可視/不可視
    this._visibility = false;

    //在中のプレイヤー
    this._players = {}

	//色設定
	this._fillColorStack = [["UNKNOWN",  [100, 100, 100, 1]]];
}

//描写
Hex.prototype.render = function(context, half_len, delta_v, draw_icon=false) {

	//左上の頂点から時計回りに線を引く
	var x = this._pos_x - half_len;
	var y = this._pos_y - delta_v;

	context.save();

	context.beginPath();
	context.moveTo(x, y);

	x += half_len * 2;
	context.lineTo(x, y);

	x += half_len;
	y += delta_v;
	context.lineTo(x, y);

	x -= half_len;
	y += delta_v;
	context.lineTo(x, y);

	x -= half_len * 2;
	context.lineTo(x, y);

	x -= half_len;
	y -= delta_v;
	context.lineTo(x, y);

	x += half_len;
	y -= delta_v;
	context.lineTo(x, y);

	context.closePath();


	//ヘックスに設定されたスタック末尾の色で描写
    var color = "rgba(";

    //rgb取得
    for(var i =0; i < 3 ; i++){
        color += this._fillColorStack[this._fillColorStack.length - 1][1][i];
        color += ",";
    }

    //可視範囲の場合alphaを低く
    color = this._visibility ?
        color + "0.4)" :
        color + this._fillColorStack[this._fillColorStack.length - 1][1][3] + ")";
    context.fillStyle = color;
	context.fill();

	//枠線を表示
	context.stroke();

    //notionがあればそれだけ表示して終了
    if(this._notion != undefined){
        print("this._notion = " + this._notion);
        context.strokeText(this._notion,
                           this._pos_x,
                           this._pos_y);
        context.restore();
        return;
    }

	//グリッド座標を表示
	context.lineWidth = 1;
	context.strokeText("(" + this._hex_id[0] + ", " + this._hex_id[1] + ")", this._pos_x - 15, this._pos_y);

    //在中プレイヤーのicon描写
    if(draw_icon){

        //iconを描写する矩形
        var x = this._pos_x - half_len;
        var y = this._pos_y - delta_v;
        var w = half_len * 2;
        var h = delta_v * 2;

        //icon描写
        var keys = Object.keys(this._players);
        switch(keys.length){

            case(0):
                break;

            case(1):
                var x = this._pos_x - half_len;
                var y = this._pos_y - half_len;
                var w = h = half_len * 2;
                context.drawImage(this._players[keys[0]]["icon"], x, y, w, h);
                break;
            case(2):

                y += (delta_v / 2);
                w = w/2;
                h = h/2;
                context.drawImage(this._players[keys[0]]["icon"], x, y, w, h);

                x += (w);
                context.drawImage(this._players[keys[1]]["icon"], x, y, w, h);

                break;

            case(3):
                //TODO:後で実装

            case(4):
                //TODO:後で実装

            //四人以上在中の時は表示がごちゃごちゃするので文字で表現
            //TODO:デフォルト画像用意する
            default:
                context.fillStyle = "rgb(255,255,255)";
                context.fillRect(x, y + delta_v /2, half_len*2, half_len*2);
                context.strokeStyle= "rgb(0, 0, 0)";
                context.strokeText("多数", this._pos_x - half_len/2, this._pos_y + half_len/2);
        }
        context.restore();
    }



}

//色登録（スタックの末尾）
Hex.prototype.set_color = function(caller, color){

    this._fillColorStack.push([caller,  color]);

}

//色削除 (スタックから削除)
//TODO: 同じcallerで二つ以上色が登録されているとFIFOになる
Hex.prototype.remove_color = function(caller){
    for(var i=0; i < this._fillColorStack.length; i++){
        if(this._fillColorStack[i][0] === caller){
            this._fillColorStack.splice(i,1);
        }
    }
}

//地形設定
//Unknownで不可視ヘックス
Hex.prototype.change_type = function(type){

    if(type == undefined){
        return;
    }

    //前の地形を削除
    this.remove_color(this._type);
    var ex_type = this._type;
    this._type = type;

    //新しい地形をセット
    switch(type){

        case("capital") :
            this.set_color("capital", [200, 0, 0, 0.8]);
            break;

        case("desert") :
            this.set_color("desert", [255, 255, 0, 0.8]);
            break;

        case("liver") :
            this.set_color("liver", [0, 50, 200, 0.8]);
            break;

        case("plain") :
            this.set_color("plain", [150, 150, 80, 0.8]);
            break;

        default:
            print("Error: 未定義の地形. [" + this._hex_id[0] + ", " + this._hex_id[1] + "]");
    }
}

//可視：true 不可視: false
Hex.prototype.set_status = function(status){

    this._visibility = status;

    //可視状態でないならプレイヤーを削除
    if(!status){
        for(var name in this._players){
            this.remove_player(name);
        }
        this._players = {};
    }
}

//最優先で表示される文字
Hex.prototype.set_notion = function(notion){
    this._notion= notion;
}

//最優先で表示される文字解除
Hex.prototype.remove_notion = function(){
    this._notion= undefined;
}

//存在するプレイヤーを設定
Hex.prototype.add_player = function(name, player_info){
    this._players[name] = player_info;
}

//プレイヤーが離れた
Hex.prototype.remove_player = function(name){

    //ヘックスから削除
    delete this._players[name];

}