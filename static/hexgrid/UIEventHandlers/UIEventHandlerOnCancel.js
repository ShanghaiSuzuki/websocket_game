
onCancel : {

    UIEventHandler.createOnCancel = function(message){
        new UIEventHandler.onCancel(message);
    }

    UIEventHandler.onCancel = function(message){

        // 親のコンストラクタ呼び出し
        UIEventHandler.Base.call(this, hex_grid.stage);

        // ボタンのリスト
        this.btnList = new UIElementHelper.BottonList(this.UIRootContainer);

        // OKボタン
        var cancelBtnContainer = UIElementHelper.createBotton("OK");
        this.btnList.addBtn(cancelBtnContainer);
        cancelBtnContainer.on("pressup", function(){
            // UI削除
            this.kill();
        }.bind(this));

        // メッセージ表示
        this.messageBox =  new UIElementHelper.MessageBox(this.UIRootContainer, 200, 200);
        this.messageBox.setText(message["reason"]);
        this.messageBox.container.x = ($("#field").width() - this.messageBox.width)/2;
        this.messageBox.container.y = ($("#field").height() - this.messageBox.height)/2;
        this.stage.update();
    }

    // prototype継承
    UIEventHandler.onCancel.prototype = Object.create(UIEventHandler.Base.prototype, {value: {constructor: UIEventHandler.onCancel}});
}