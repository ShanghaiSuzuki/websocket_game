
onNotify : {

    UIEventHandler.createOnNotify = function(message){
        new UIEventHandler.onNotify(message);
    }

    UIEventHandler.onNotify = function(message){

        // 親のコンストラクタ呼び出し
        UIEventHandler.Base.call(this, hex_grid.stage);

        // メッセージ表示
        this.messageBox =  new UIElementHelper.MessageBox(this.UIRootContainer, 200, 200);
        this.messageBox.setText(message["message"]);
        this.messageBox.container.x = ($("#field").width() - this.messageBox.width)/2;
        this.messageBox.container.y = ($("#field").height() - this.messageBox.height)/2;
        this.stage.update();
    }

    // prototype継承
    UIEventHandler.onNotify.prototype = Object.create(UIEventHandler.Base.prototype, {value: {constructor: UIEventHandler.onNotify}});
}