
var click_radius = 3;
//六角形のクラス
function Hex(hex_id, pos_x, pos_y, stage, container, radius) {

    this.stage = stage;
    this.container = container;
    this.radius = radius;

    // ヘックスを作成
    this.shape = new createjs.Shape();
    this.fillCmd = this.shape.graphics.beginFill("Black").command;
    this.strokeCmd = this.shape.graphics.beginStroke("Gray").command;
    this.shape.graphics.drawPolyStar(pos_x, pos_y, radius, 6, 0, 0);

    // Containerに登録
    this.hex_container = new createjs.Container();
    this.hex_container.addChild(this.shape, this.text_hex);
    this.container.addChild(this.hex_container);

	//グリッド空間の座標
	this.hex_id = hex_id;

	// ワールド空間の座標
	this._pos_x = pos_x;
	this._pos_y = pos_y;

    //不可視/不可視
    this._visibility = false;

    //在中のプレイヤー
    this._player = {}

	// イベント登録
	this.shape.addEventListener("mousedown", this.onMouseDown.bind(this));
	this.shape.addEventListener("pressup", this.onPressUp.bind(this));
	this.shape.addEventListener("pressmove", this.onPressMove.bind(this));

}

//地形設定
//Unknownで不可視ヘックス
Hex.prototype.change_type = function(type){

    if(type == undefined){
        return;
    }

    this._type = type;


}

//可視：true 不可視: false
Hex.prototype.set_status = function(visibility){

    this._visibility = visibility;

    //新しい地形をセット
    switch(this._type){

        case("capital") :
            if (visibility)
                this.fillCmd.style = "rgba(200, 0, 0, 0.5)";
            else
                this.fillCmd.style = "rgba(200, 0, 0, 0.8)";
            break;

        case("desert") :
            if (visibility)
                this.fillCmd.style = "rgba(255, 255, 0, 0.5)";
            else
                this.fillCmd.style = "rgba(255, 255, 0, 0.8)";
            break;

        case("liver") :
            if (visibility)
                this.fillCmd.style = "rgba(0, 50, 200, 0.5)";
            else
                this.fillCmd.style = "rgba(0, 50, 200, 0.8)";
            break;

        case("plain") :
            if (visibility)
                this.fillCmd.style = "rgba(150, 150, 80, 0.5)";
            else
                this.fillCmd.style = "rgba(150, 150, 80, 0.8)";
            break;

        default:
            print("Error: 未定義の地形. [" + this.hex_id[0] + ", " + this.hex_id[1] + "]");
    }
    // 不可視領域への変更なら在中プレイヤーを削除
    if(!status)
        this.remove_player();
}

// ヘックスの座標を表示
Hex.prototype.show_id = function(){

    if (!this.text){
        this.text = new createjs.Text(this.hex_id[0] + ", " + this.hex_id[1], this.radius/2+"px sans-serif", "Black");
        this.text.x = this._pos_x;
        this.text.y = this._pos_y;
    }
    this.hex_container.addChild(this.text);
}

// ヘックスに在中プレイヤーを追加
Hex.prototype.add_player = function(player_info){

    this._player = player_info;

    var img = new Image();
    img.src =  "static/resource/icon/" + player_info["icon_id"] +".jpeg"
    img.onload = function(){
        print("img onload");
        this.bitmap = new createjs.Bitmap(img);
        this.hex_container.addChild(this.bitmap);
        this.bitmap.x = this._pos_x - hex_grid.half_len;
        this.bitmap.y = this._pos_y - hex_grid.delta_v / 2;
        this.stage.update();
    }.bind(this);
}

Hex.prototype.remove_player = function(name, player_info){
    if (this._player != null){
        // 画像アンロード
        this.hex_container.removeChild(this.bitmap);
        delete this.bitmap;
        delete this_player;
        this.stage.update();
    }
}

// Hexを選択状態に
Hex.prototype.onSelected = function(){
    this.strokeExStyle = this.strokeCmd.style;
    this.strokeCmd.style = "rgba(255, 0, 0, 1)";
    this.container.addChild(this.hex_container);
    this.stage.update();
}

// Hexの選択状態を解除
Hex.prototype.onDeselected = function(){

    this.strokeCmd.style = this.strokeExStyle;
    this.container.addChild(this.hex_container);
    this.ex_pos_x = null;
    this.ex_pos_y = null;
    this.stage.update();

}

Hex.prototype.onMouseDown = function(e){

    e.preventDefault();
    e.stopPropagation();

    // 選択状態True
    this.onSelected();

    // クリック判定用にマウスダウン時の座標を保存
    this.down_stage_x = e.stageX;
    this.down_stage_y = e.stageY;

}

Hex.prototype.onPressUp = function(e){

    e.preventDefault();
    e.stopPropagation();

    // 選択状態解除
    this.onDeselected();

    // クリック判定 ダウンとアップが指定の範囲内で行われた場合
    if ( Math.abs(this.down_stage_x  - e.stageX) <= click_radius * this.container.scaleX ){
        var handler = new UIEventHandler.onClickHex(this.stage, this);
    }
}

Hex.prototype.onPressMove = function(e){
    e.preventDefault();
    e.stopPropagation();

    if (this.ex_pos_x == null){
        this.ex_pos_x = e.stageX;
        this.ex_pos_y = e.stageY;
        return;
    }

    var diff_x = e.stageX - this.ex_pos_x;
    var diff_y = e.stageY - this.ex_pos_y;
    this.ex_pos_x = e.stageX;
    this.ex_pos_y = e.stageY;
    this.container.regX -= diff_x / this.container.scaleX;
    this.container.regY -= diff_y / this.container.scaleY;
    this.stage.update();

}
