
OnClickHex: {
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
            socket.bindHandler("response_hexinfo", UIEventHandler.OnResponseHexInfo.bind(this, this.stage, this.hex));
            socket.send("request_hexinfo", {"col" : this.hex.hex_id[0], "row" : this.hex.hex_id[1]});

            // UI削除
            this.kill();

        }.bind(this));

        stage.update();
    }
    // 継承
    UIEventHandler.OnClickHex.prototype = Object.create(UIEventHandler.Base.prototype, {value: {constructor: UIEventHandler.OnClickHex}});

    var p = UIEventHandler.OnClickHex.prototype;
    p.kill = function(){
        this.hex.onDeselected();
        UIEventHandler.Base.prototype.kill.call(this);
    }
}

// サーバーからresponse_hexinfoイベント受信
OnResponseHexInfo: {

    UIEventHandler.OnResponseHexInfo = function(stage, hex, data){

        // 親のコンストラクタ呼び出し
        UIEventHandler.Base.call(this, stage);

        // 受信したデータを保持
        this.data = data

        // ボタンのリスト
        this.btnList = new UIElementHelper.BottonList(this.UIRootContainer);

        // ヘックスを選択状態に
        this.hex = hex;
        hex.onSelected();

        // キャンセルボタン
        var cancelBtnContainer = UIElementHelper.createBotton("キャンセル");
        this.btnList.addBtn(cancelBtnContainer);
        cancelBtnContainer.on("pressup", function(){

            // ヘックスの選択状態解除
            this.hex.onDeselected();

            // UI削除
            UIEventHandler.Base.prototype.kill.call(this);

        }.bind(this));


        // 土地ボタン
        var terrianBtnContainer = UIElementHelper.createBotton("土地情報");
        this.btnList.addBtn(terrianBtnContainer);
        terrianBtnContainer.on("pressup", UIEventHandler.OnResponseHexInfo.prototype.showTerrianInfo.bind(this));

        // プレイヤーボタン
        if ("player_info" in data){
            var playerBtnContainer = UIElementHelper.createBotton("プレイヤー情報");
            this.btnList.addBtn(playerBtnContainer);
            playerBtnContainer.on("pressup", UIEventHandler.OnResponseHexInfo.prototype.showPlayerInfo.bind(this));
        }

        // 部隊ボタン
        if ("division_info" in data){
            print("has division_info");
            var divisionBtnContainer = UIElementHelper.createBotton("部隊情報");
            this.btnList.addBtn(divisionBtnContainer);
            divisionBtnContainer.on("pressup", UIEventHandler.OnResponseHexInfo.prototype.showDivisionInfo.bind(this));
        }
        // 最初は土地情報を表示
        UIEventHandler.OnResponseHexInfo.prototype.showTerrianInfo.bind(this)();
        this.stage.update();
    }

    var p = UIEventHandler.OnResponseHexInfo.prototype;

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


