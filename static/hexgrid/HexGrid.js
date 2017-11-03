//とりあえずブラウザ画面への出力用
function print(message){
    var messages = $("#text_box").val();
	$("#text_box").val(message + "\n" + messages);
}

//HexとCanvasを管理するクラス
//ヘックスの一辺の長さとフィールドの広さからヘックスグリッドを定義する
function HexGrid(socket) {

	print("HexGrid: in constructor : ver 0.11");

    // CSSで伸ばしたcanvasはcanvasを引き延ばしただけなので、その高さと幅をDOMのcanvasに再設定する
	this.canvas_width = $("#field").width();
	this.canvas_height = $("#field").height();
    this.canvas = document.getElementById("field");
    this.canvas.width = this.canvas_width;
    this.canvas.height = this.canvas_height;

	//canvas上のプレイヤー
	this.players = {};

	//自身の情報
	this._self_info = [];

	// 辺の長さ
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

	//ソケット
	this.socket = socket;

	//initはwebsocketのハンドラとして起動する
	this.socket.bindHandler("init_hexgrid", this.init.bind(this));

	//更新用のハンドラ
    this.socket.bindHandler("update_hexgrid", this.update.bind(this));

    //サーバにリクエストを送信し初期化開始
	this.socket.send("init_hexgrid", {});

}


HexGrid.prototype.init = function(data)
{
    //フィールドの広さを定義する三つの変数
	this.width = data["width"];
	this.height = data["height"];
	this.length = data["length"];

	// スケーリングの初期値はヘックスが横に10個入るスケール
	this.scale = this.canvas_width / this.width;

    //　ステージにヘックスグリッドを追加
    this.stage = new createjs.Stage("field");
    createjs.Touch.enable(this.stage); // タッチ対応
    this.world = new createjs.Container();
    this.world.scaleX = this.scale;
    this.world.scaleY = this.scale;
    this.stage.addChild(this.world);

    // ステージに＋-のスケールボタンを追加
    var btn_radius = this.canvas_width * 0.03;
    this.btn_minus_scale = new createjs.Shape();
    this.btn_minus_scale.graphics.beginFill("Red").drawCircle(btn_radius, btn_radius, btn_radius);
    this.btn_minus_scale.on("click", function(e){ e.stopPropagation(); this.func_scale(false);}, this);
    this.btn_plus_scale = new createjs.Shape();
    this.btn_plus_scale.graphics.beginFill("Blue").drawCircle(btn_radius, btn_radius*3, btn_radius);
    this.btn_plus_scale.on("click", function(e){e.stopPropagation(); this.func_scale(true);}, this);
    this.stage.addChild(this.btn_minus_scale);
    this.stage.addChild(this.btn_plus_scale);

	// ヘックスの大きさの定義
	this.half_len = this.length / 2; // 正六角形の一辺の長さの半分
	this.delta_v = this.length * Math.sin(1 / 3 * Math.PI); // 正六角形の高さの半分

	//平行移動の制限
	this.translate_min = [-this.width + this.canvas_width, -this.height + this.canvas_height];

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

            // CreateJSのShapeを生成してworldに登録
			var hex = new Hex([g_col, g_row], x, y, this.stage, this.world, this.half_len*2);
			this.hexagons[i_col][i_row] = hex;
			y += delta_y * 2;
		}

		x += delta_x;
		col++;

	}

    //自身の情報を設定
    this._self_info["name"] = data["name"];
    this._self_info["col"] = data["col"];
    this._self_info["row"] = data["row"];
    this._self_info["country"] = data["country"];

    //描写情報更新
    this.update(data);

    print("HexGrid初期化完了");


}
//ヘックスグリッドが更新された時のハンドラ
HexGrid.prototype.update = function(data){

    print("in HexGrid.update");

    // 移動したプレイヤーがいる場合
    if ("moving_player" in data){

        // 元のヘックスから削除
        ex_col = data["moving_player"]["ex_col"];
        ex_row = data["moving_player"]["ex_row"];
        var index = this._gridToIndex([ex_col, ex_row]);
        this.hexagons[index[0]][index[1]].remove_player(data["moving_player"]["user_id"]);

        // 新しいヘックスに追加
        new_col = data["moving_player"]["new_col"];
        new_row = data["moving_player"]["new_row"];
        var index = this._gridToIndex([new_col, new_row]);
        this.hexagons[index[0]][index[1]].add_player(data["moving_player"]);
    }

    //可視になった領域を読み込み
    if ("visible_area" in data){
        data["visible_area"].forEach(function(hex){
            var index = this._gridToIndex([hex["col"], hex["row"]]);
            this.hexagons[index[0]][index[1]].change_type(hex["type"]);
            this.hexagons[index[0]][index[1]].set_status(true);
        }.bind(this));
    }

    //不可視になった領域を読み込み
    if ("unvisible_area" in data){
        data["unvisible_area"].forEach(function(hex){
            var index = this._gridToIndex([hex["col"], hex["row"]]);
            var target = this.hexagons[index[0]][index[1]];
            target.change_type(hex["type"]);
            target.set_status(false);
        }.bind(this));
    }

    // 新しく現れたプレイヤーを読み込み
    if ("new_players" in data){

        data["new_players"].forEach(function(new_player){
            var index = this._gridToIndex([new_player["col"], new_player["row"]]);
            this.hexagons[index[0]][index[1]].add_player(new_player);
        }.bind(this));
    }

    // 不可視になったプレイヤーを読み込み、削除
    if ("removed_players" in data){

        data["removed_players"].forEach(function(removed_player){
            var index = this._gridToIndex([removed_player["col"], remove_player["row"]]);
            var name = removed_player["user_name"];
            this.hexagons[index[0]][index[1]].removed_player_player(name);
        }.bind(this));
    }

    // 描写領域をアップデート
    this.stage.update();
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

HexGrid.prototype.func_scale = function(isPlus){

    var old_scale = this.scale;
    if (isPlus)
        this.scale += 0.1;
    else
        this.scale -= 0.1;

    print("func_scale " + this.scale);
    this.world.scaleX = this.scale;
    this.world.scaleY = this.scale;

    // 現在の中心座標　＝　コンテナの平行移動　＋　画面内の平行移動(コンテナの平行移動+canvas_x[y]/2*scale)
    // コンテナの平行移動分をスケーリング
    this.world.regX -= (this.canvas_width/2) * (old_scale - this.scale)
    this.world.regY -= (this.canvas_height/2) * (old_scale - this.scale);

    print(this.world.x + " " + this.world.y);




    this.stage.update();
}

