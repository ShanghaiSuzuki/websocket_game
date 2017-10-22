
var click_radius = 3;
//六角形のクラス
function Hex(hex_id, pos_x, pos_y, stage, container, radius) {

    this.stage = stage;
    this.container = container;

    // shapeを作成してステージに追加
    this.shape = new createjs.Shape();
    this.fillCmd = this.shape.graphics.beginFill("Black").command;
    this.strokeCmd = this.shape.graphics.beginStroke("Gray").command;
    this.shape.graphics.drawPolyStar(pos_x, pos_y, radius, 6, 0, 0);

    // BitmapとShapeのためのContainer
    this.hex_container = new createjs.Container();
    this.hex_container.addChild(this.shape);

    this.container.addChild(this.hex_container);


	//グリッド空間の座標
	this._hex_id = hex_id;

	// ワールド空間の座標
	this._pos_x = pos_x;
	this._pos_y = pos_y;

    //地形
    this._type = "UNKNOWN";

    //不可視/不可視
    this._visibility = false;

    //在中のプレイヤー
    this._player = {}

	//色設定
	this._fillColorStack = [["UNKNOWN",  [100, 100, 100, 1]]];

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
            print("Error: 未定義の地形. [" + this._hex_id[0] + ", " + this._hex_id[1] + "]");
    }
    // 不可視領域への変更なら在中プレイヤーを削除
    if(!status){
    /*
        while (this._players.length != 0){
            delete this._players[this._players.length - 1];
        }
    */
    }
}

// ヘックスに在中プレイヤーを追加
Hex.prototype.add_player = function(player_info){

    print("add player");
    this._player = player_info;

    var img = new Image();
    img.src = player_info["icon"];
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

Hex.prototype.onMouseDown = function(e){

    e.preventDefault();
    e.stopPropagation();

    // 選択状態ストロークを赤く
    this.strokeExStyle = this.strokeCmd.style;
    this.strokeCmd.style = "rgba(255, 0, 0, 1)";
    this.container.addChild(this.hex_container);
    this.stage.update();

    // クリック判定用にマウスダウン時の座標を保存
    this.down_stage_x = e.stageX;
    this.down_stage_y = e.stageY;

}

Hex.prototype.onPressUp = function(e){

    e.preventDefault();
    e.stopPropagation();

    // 選択状態解除。ストロークを元の色に
    this.strokeCmd.style = this.strokeExStyle;
    this.container.addChild(this.hex_container);
    this.ex_pos_x = null;
    this.ex_pos_y = null;
    this.stage.update();

    // クリック判定 ダウンとアップが指定の範囲内で行われた場合
    if ( Math.abs(this.down_stage_x  - e.stageX) <= click_radius * this.container.scaleX ){
        var handler = new UIEventHandlerBase(this.stage);
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
