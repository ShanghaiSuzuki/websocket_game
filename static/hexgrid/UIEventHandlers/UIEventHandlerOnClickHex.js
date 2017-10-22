
UIEventHandler.OnClickHex = function(stage, hex){

    // 親のコンストラクタ呼び出し
    UIEventHandler.Base.call(this, stage);

    // Hexを選択状態に
    this.hex = hex;
    this.hex.onSelected();

    // ボタンのリスト
    this.btnList = new UIElementHelper.BottonList(this.UIRootContainer);

    // キャンセルボタン
    var cancelBtnContainer = UIElementHelper.createBotton("キャンセル");
    this.btnList.addBtn(cancelBtnContainer);
    cancelBtnContainer.on("pressup", function(){
        // UI削除
        this.hex.onDeselected();
        this.kill();
    }.bind(this));

    // 情報ボタン
    var hexinfoBtn = UIElementHelper.createBotton("情報");
    this.btnList.addBtn(hexinfoBtn);
    hexinfoBtn.on("pressup", function(){

        // サーバにこのhexの情報を要求
        print("UIEHOC hex_id = " + this.hex.hex_id);
        socket.send("request_hexinfo", {"col" : this.hex.hex_id[0], "row" : this.hex.hex_id[1] });

        // UI削除
        this.hex.onDeselected();
        this.kill();
    }.bind(this));

    stage.update();
}

// 継承
  Object.setPrototypeOf(UIEventHandler.OnClickHex.prototype, UIEventHandler.Base.prototype);
