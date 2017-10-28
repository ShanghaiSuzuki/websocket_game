//　ステージの一番上のスタックに新しいコンテナが現れ、入力イベントをフックする
//  コンテナ挿入の演出もここで書く
var UIEventHandler = {
};

UIEventHandler.Base = function(stage){

    this.stage = stage;
	this.canvas_width = $("#field").width();
	this.canvas_height = $("#field").height();

    // UIコンテナを作成
    // UIEventHandlerBaseを継承したハンドラはここにDisplayObjectを追加する
    this.UIRootContainer = new createjs.Container();

    // UIコンテナをステージに追加
    this.stage.addChild(this.UIRootContainer);

    // UI用の矩形が画面を覆い、下のレイヤーへのインプットを抑制
	this.UIRect = new createjs.Shape();
    this.UIRectFillCmd = this.UIRect.graphics.beginFill("rgba(100, 0, 100, 0.5)").command;
    this.UIRectStrokeCmd = this.UIRect.graphics.beginStroke("Gray").command;
    this.UIRect.graphics.drawRect(0, 0, this.canvas_width, this.canvas_height);
    this.UIRootContainer.addChild(this.UIRect);
    this.UIRect.on("mousedown", function(){});

    this.stage.update();
}

UIEventHandler.Base.prototype = {

    // 削除
    kill : function(){

        this.stage.removeChild(this.UIRootContainer);
        delete this.UIRootContainer;
        this.stage.update();
        delete this;
    }
}

