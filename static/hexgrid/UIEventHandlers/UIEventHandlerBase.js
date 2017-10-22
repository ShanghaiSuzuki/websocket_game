
function UIEventHandlerBase(stage){

    //　ステージの一番上のスタックに新しいコンテナが現れ、入力イベントをフックする
    //  コンテナ挿入の演出もここで書く
    this.stage = stage;
	this.canvas_width = $("#field").width();
	this.canvas_height = $("#field").height();

	// ＵＩ用の矩形領域
	this.shape = new createjs.Shape();
    this.fillRectCmd = this.shape.graphics.beginFill("rgba(100, 100, 0, 0.2)").command;
    this.strokeRectCmd = this.shape.graphics.beginStroke("Gray").command;
    this.shape.graphics.drawRect(0, 0, this.canvas_width, this.canvas_height);

    // UIコンテナ
    this.UIEvent_container = new createjs.Container();
    this.UIEvent_container.addChild(this.shape);

    this.stage.addChild(this.UIEvent_container);
    this.stage.update();


}

UIEventHandlerBase.init = function(stage){


}