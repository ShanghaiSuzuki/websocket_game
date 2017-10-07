function BBSCountry(socket){

    //内容(jqueryオブジェクトのキュー)
    this._articles = undefined;

    //名前とicon（hexgridと重複するが管理が難しいので独立して保持する）
    this._icons = {};

    //cssを読み込み
    var style = '<link rel="stylesheet" href="static/hexgrid/BBSCountry.css?var=1dadws">';
    $('head link:last').after(style);

    //会議室ウィンドウ作成
    $("#tab-3").append("<div id=\"bbs_country_container\"></div>");
    $("#bbs_country_container").addClass("bbs_country_container");

    //発言ウィンドウ追加
    $("#bbs_country_container").append("<div id=write_window></div");
    $("<textarea id=\"write_box\" cols=\"20\" rows=\"5\">").addClass("write_box").appendTo("#write_window");
    $("<button>").addClass("write_button").text("書き込み").click(function(){
       this.write($(".write_box").val());
    }.bind(this)).appendTo("#write_window");

    this.socket = socket;
    this.socket.bindHandler("init_bbs_country", this.init.bind(this));
    this.socket.bindHandler("update_bbs_country", this.update.bind(this));
    this.socket.send("init_bbs_country", "");
}

//初期化
BBSCountry.prototype.init= function(data){

    //既存の発言クリア
    $("#bbs_country_container div#article_window").empty();
    $("<div id=article_window>").addClass("article_window").appendTo("#bbs_country_container");

    //発言を埋める
    for(var i=data.length-1; i >= 0; i--){
        this.addArticle(data[i]);
    }
}

//新しいメッセージを受け取るハンドラ
BBSCountry.prototype.update= function(data){
    print("BBSCountry.update() called");

    //発言が20以上で入れ替え
    /*
    var counter = 0;
    $('li').each(function(){
        counter++;
    });
    if(this.articles.length > 20){

        //一番古いのを削除
        $("#bbs_country_container div.article:last").empty();

    }
    */

    //発言を追加
    this.addArticle(data);

}

//DOM要素に発言を追加
BBSCountry.prototype.addArticle = function(data){

    //iconが無ければロード
    if(!this._icons[data["name"]]){
        var icon = new Image();
        icon.src = "static/resource/icon/" + data["icon"] +".jpeg";
        print(data["name"]);
        this._icons[data["name"]] = icon;
    }

    var $container = $("<div>");
    $container
    .addClass("article")
    .append($(this._icons[data["name"]]).clone())
    .append($("<p class=\"name\"></p>"))
    .append($("<p class=\"date\"></p>"))
    .append($("<p class=\"message\"></p>"));

    $container.children(".message").html(data["article"]);
    $container.children(".date").text(data["date"]);
    $container.children(".name").text(data["name"]);

    $("#article_window").prepend($container);
}

//書き込み
BBSCountry.prototype.write = function(message){

    this.socket.send("write_bbs_country", message);
    HexGridMessage.open("送信しました", "反映されるまでお待ちください")
    $("#write_box").val("");

}