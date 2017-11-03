// ヘックスクリック時のハンドラ
onClickHex: {
    UIEventHandler.onClickHex = function(stage, hex){

        // 親のコンストラクタ呼び出し
        UIEventHandler.Base.call(this, stage);

        // Hexを選択状態に
        this.hex = hex;
        this.hex.onSelected();

        // ボタンのリスト
        this.btnList = new UIElementHelper.BottonList(this.UIRootContainer);

        // 情報ボタン
        var hexinfoBtn = UIElementHelper.createBotton("情報");
        this.btnList.addBtn(hexinfoBtn);
        hexinfoBtn.on("pressup", function(){

            // サーバにこのhexの情報を要求
            socket.bindHandler("response_hexinfo", UIEventHandler.onResponseHexInfo.bind(this, this.stage, this.hex));
            socket.send("request_hexinfo", {"col" : this.hex.hex_id[0], "row" : this.hex.hex_id[1]});

            // UI削除
            this.kill();

        }.bind(this));

        // 進軍問い合わせボタン
        var moveBtn = UIElementHelper.createBotton("進軍調査");
        this.btnList.addBtn(moveBtn);
        moveBtn.on("pressup", function(){

            // サーバに進軍可能か問い合わせ
            socket.bindHandler("response_ask_move", UIEventHandler.onResponseAskMove.bind(this, this.stage, this.hex));
            socket.send("ask_move", {"col" : this.hex.hex_id[0], "row" : this.hex.hex_id[1]});

            // UI削除
            this.kill();
        }.bind(this));

        stage.update();
    }

    // 継承
    UIEventHandler.onClickHex.prototype = Object.create(UIEventHandler.Base.prototype, {value: {constructor: UIEventHandler.onClickHex}});

    var p = UIEventHandler.onClickHex.prototype;
    p.kill = function(){
        this.hex.onDeselected();
        UIEventHandler.Base.prototype.kill.call(this);
    }
}

// 情報クリック時のハンドラ(サーバからのイベントで呼び出し）
onResponseHexInfo: {

    UIEventHandler.createOnResponseHexInfo = function(stage, hex, data){
    }

    UIEventHandler.onResponseHexInfo = function(stage, hex, data){

        // 親のコンストラクタ呼び出し
        UIEventHandler.Base.call(this, stage);

        // 受信したデータを保持
        this.data = data

        // ボタンのリスト
        this.btnList = new UIElementHelper.BottonList(this.UIRootContainer);

        // ヘックスを選択状態に
        this.hex = hex;
        hex.onSelected();

        // 土地ボタン
        var terrianBtnContainer = UIElementHelper.createBotton("土地情報");
        this.btnList.addBtn(terrianBtnContainer);
        terrianBtnContainer.on("pressup", UIEventHandler.onResponseHexInfo.prototype.showTerrianInfo.bind(this));

        // プレイヤーボタン
        if ("player_info" in data){
            var playerBtnContainer = UIElementHelper.createBotton("プレイヤー情報");
            this.btnList.addBtn(playerBtnContainer);
            playerBtnContainer.on("pressup", UIEventHandler.onResponseHexInfo.prototype.showPlayerInfo.bind(this));
        }

        // 部隊ボタン
        if ("division_info" in data){
            print("has division_info");
            var divisionBtnContainer = UIElementHelper.createBotton("部隊情報");
            this.btnList.addBtn(divisionBtnContainer);
            divisionBtnContainer.on("pressup", UIEventHandler.onResponseHexInfo.prototype.showDivisionInfo.bind(this));
        }

        // 最初は土地情報を表示
        UIEventHandler.onResponseHexInfo.prototype.showTerrianInfo.bind(this)();
        this.stage.update();
    }

    var p = UIEventHandler.onResponseHexInfo.prototype;

    // 削除
    p.kill = function(){
        this.hex.onDeselected();
        UIEventHandler.Base.prototype.kill.call(this);
    }

    // 土地情報表示
    p.showTerrianInfo = function(){

        if (this.table)
            this.table.remove();

        this.table = new UIElementHelper.Table(this.UIRootContainer);
        var header = "hex_info";
        if (header in this.data){
            if("type" in this.data[header]){

                switch(this.data[header]["type"]){
                case "plain" : this.table.addRecord("地形", "平原"); break;
                case "liver" : this.table.addRecord("地形", "川"); break;
                case "capital" : this.table.addRecord("地形", "首都"); break;
                default: this.table.addRecord("地形", this.data["hex_info"]["type"]);
                }
            }

            if("food" in this.data[header])
                this.table.addRecord("食糧生産", this.data["hex_info"]["food"]);

            if("money" in this.data[header])
                this.table.addRecord("資金生産", this.data["hex_info"]["money"]);

            if("soldier" in this.data[header])
                this.table.addRecord("兵士生産", this.data["hex_info"]["soldier"]);
        }
        else{
                this.table.addRecord("情報なし", "");
        }

        // テーブル内部のオフセットを計算して位置調整
        this.table.calc();
        this.table.container.x = ($("#field").width() - this.table.width)/2;
        this.table.container.y = ($("#field").height() - this.table.height)/2;

        this.stage.update();
    }

    // プレイヤー情報表示
    p.showPlayerInfo = function(){

        if (this.table)
            this.table.remove();
        this.table = new UIElementHelper.Table(this.UIRootContainer);

        var player_info = this.data["player_info"]
        if("player_name" in player_info)
            this.table.addRecord("名前", player_info["player_name"]);
        if("country_name" in player_info)
            this.table.addRecord("国", player_info["country_name"]);

        // テーブル内部のオフセットを計算して位置調整
        this.table.calc();
        this.table.container.x = ($("#field").width() - this.table.width)/2;
        this.table.container.y = ($("#field").height() - this.table.height)/2;

        this.stage.update();
    }

    // 部隊情報表示
    p.showDivisionInfo = function(){

        print("showDivisionInfo");
        if (this.table)
            this.table.remove();

        this.table = new UIElementHelper.Table(this.UIRootContainer);
        var division_info = this.data["division_info"];
        if("division_name" in division_info)
            this.table.addRecord("部隊名", division_info["division_name"]);
        if("branch_name" in division_info)
            this.table.addRecord("兵科", division_info["branch_name"]);
        if("level" in division_info)
            this.table.addRecord("レベル", division_info["level"]);
        if("quantity" in division_info)
            this.table.addRecord("兵数", division_info["quantity"]);
        if("status" in division_info)
            this.table.addRecord("status", division_info["status"]);

        // テーブル内部のオフセットを計算して位置調整
        this.table.calc();
        this.table.container.x = ($("#field").width() - this.table.width)/2;
        this.table.container.y = ($("#field").height() - this.table.height)/2;

        this.stage.update();
    }
}

// 進軍調査クリック時のハンドラ（サーバイベントで呼び出し）
onResponseAskMove: {
    UIEventHandler.onResponseAskMove = function(stage, hex, data){

        // 親のコンストラクタ呼び出し
        UIEventHandler.Base.call(this, stage);

        // 受信したデータを保持
        this.data = data;

        // ヘックスを選択状態に
        this.hex = hex;
        hex.onSelected();

        // ボタンのリスト
        this.btnList = new UIElementHelper.BottonList(this.UIRootContainer);

        // 進軍不可の時
        if (data["response"] == "deny"){
            this.messageBox =  new UIElementHelper.MessageBox(this.UIRootContainer, 200, 200);
            this.messageBox.setText(data["reason"]);
            this.messageBox.container.x = ($("#field").width() - this.messageBox.width)/2;
            this.messageBox.container.y = ($("#field").height() - this.messageBox.height)/2;
            this.stage.update();
        }

        // 進軍可能な時
        else if(data["response"] == "accept"){

            print("accept");

            // 進軍ボタン追加
            var moveBtnContainer = UIElementHelper.createBotton("進軍");
            this.btnList.addBtn(moveBtnContainer);
            moveBtnContainer.on("pressup", function(){

                // サーバに進軍リクエストを送信
                socket.bindHandler("response_request_move", UIEventHandler.createOnResponseRequestMove.bind(this, this.stage));
                socket.send("request_move", {"col" : this.hex.hex_id[0], "row" : this.hex.hex_id[1]});

                // ヘックスの選択状態解除
                this.hex.onDeselected();

                // UI削除
                this.kill();

            }.bind(this));

            // 所要時間など表示
            this.table = new UIElementHelper.Table(this.UIRootContainer);
            this.table.addRecord("所要時間", data["required_time"] / 3600 + "分");
            this.table.addRecord("消費食糧", data["food"]);
            this.table.addRecord("消費資金", data["money"]);

            // テーブル内部のオフセットを計算して位置調整
            this.table.calc();
            this.table.container.x = ($("#field").width() - this.table.width)/2;
            this.table.container.y = ($("#field").height() - this.table.height)/2;

            this.stage.update();
        }
    }


    var p = UIEventHandler.onResponseHexInfo.prototype;

    p.kill = function(){
        this.hex.onDeselected();
        UIEventHandler.Base.prototype.kill.call(this);
    }

}

OnResponseRequestMove: {

    UIEventHandler.createOnResponseRequestMove = function(stage, data){
        var ui = new UIEventHandler.onResponseRequestMove(stage, data);
    }

    UIEventHandler.onResponseRequestMove = function(stage, data){

        // 親のコンストラクタ呼び出し
        UIEventHandler.Base.call(this, stage);

        // 到着時刻表示
        this.messageBox =  new UIElementHelper.MessageBox(this.UIRootContainer, 200, 200);
        var _message = "進軍を開始した。\n到着時刻 : ";
        this.messageBox.setText(_message + data["arrival_time"]);
        this.messageBox.container.x = ($("#field").width() - this.messageBox.width)/2;
        this.messageBox.container.y = ($("#field").height() - this.messageBox.height)/2;
        this.stage.update();

        this.stage.update();
        okBtnContainer.on("pressup", function(){
            this.kill();
        }.bind(this));
    }

    // 継承
    UIEventHandler.onResponseRequestMove.prototype = Object.create(UIEventHandler.Base.prototype, {value: {constructor: UIEventHandler.onResponseRequestMove}});
    var p = UIEventHandler.onResponseRequestMove.prototype;

    p.kill = function(){
        UIEventHandler.Base.prototype.kill.call(this);
    }
 }
