//　ステージの一番上のスタックに新しいコンテナが現れ、入力イベントをフックする
//  コンテナ挿入の演出もここで書く
var UIEventHandler = {};

UIEventHandler.Base = function(stage){

    this.stage = stage;
	this.canvas_width = $("#field").width();
	this.canvas_height = $("#field").height();

    // UIコンテナを作成
    // UIEventHandlerBaseを継承したハンドラはここにDisplayObjectを追加する
    this.UIRootContainer = new createjs.Container();

	// ＵＩ用の矩形領域
	this.UIRect = new createjs.Shape();
    this.UIRectFillCmd = this.UIRect.graphics.beginFill("rgba(100, 0, 100, 0.5)").command;
    this.UIRectStrokeCmd = this.UIRect.graphics.beginStroke("Gray").command;
    this.UIRect.graphics.drawRect(0, 0, this.canvas_width, this.canvas_height);
    this.UIRootContainer.addChild(this.UIRect);

    // UI用の矩形領域はクリックをフックして抑制する
    this.UIRect.on("mousedown", function(){});

    // UIコンテナをステージに追加
    this.stage.addChild(this.UIRootContainer);
    this.stage.update();

    print("UIHB constructor end");
    print("this.stage = " + stage);

}

// 削除
UIEventHandler.Base.prototype.kill = function(){
    this.stage.removeChild(this.UIRootContainer);
    delete this.UIRootContainer;
    this.stage.update();
    delete this;
}

