//メッセージハンドラ登録機能を持ったwebsocketのwrapper
function BJSocket(url, text_callback){

  this.url = url;
  this.text_callback = text_callback ||
					   function(message){ console.log(message); };

  //接続が切れた場合の再接続の設定
  this.max_reconnect_count = 10;
  this.recconect_count = 0;
  this.recconect_interval = 3000;//ms

  this.handlers = {};

}

//初期化
BJSocket.prototype.init = function(){

	this.websocket = new WebSocket(this.url);
	this.websocket.onopen = this.onOpen.bind(this);
	this.websocket.onclose = this.onClose.bind(this);
	this.websocket.onerror= this.onError.bind(this);
	this.websocket.onmessage= this.onMessage.bind(this);
}

//websocket自体のイベントハンドラ
BJSocket.prototype.onOpen = function(e){

	//再接続のトライ回数リセット
	this.recconect_count = 0;

	this.text_callback("接続");

}

BJSocket.prototype.onClose= function(e){

	this.text_callback("通信が途絶した。" + this.recconect_interval/1000.0 + "秒後に再接続");

	//再接続
	this.recconect_count++;
	if(this.recconect_count > this.max_reconnect_count){
		this.text_callback("トライ回数が最大値に達した。少し待ってから再接続して下さい。");
		return;
	}
	else{
	    //TODO: initじゃなくてwebsocketの再接続だけで良い
		setTimeout(this.init.bind(this), 3000);

	}
}

BJSocket.prototype.onError= function(e){

    this.text_callback("エラー");
}

BJSocket.prototype.onMessage = function(e){

	var json = JSON.parse(e.data);

	//登録されたイベントハンドラーに処理を振り分け
	this.dispatch(json.event, json.data);
}

//ブラウザからサーバーへイベント送信
BJSocket.prototype.send = function(event_name, event_data){

    var count = 0;
    var max_count = 10;
    var interval = 100;//ms
    var payload = JSON.stringify({event:event_name, data: event_data});

    //通信状況に応じて送信を待機する
    function delayedSend(){

        if(this.websocket.readyState === 1){
            this.websocket.send(payload);
            return;
        }
        else if(count > max_count){
            this.text_callback("エラー：遅延送信が最大トライ回数に達した。");
            return;
        }

        count++;
        setTimeout(delayedSend.bind(this), interval);
    }

    delayedSend.bind(this)();
    //return this;
}

//イベントの種類とハンドラを束縛、登録
BJSocket.prototype.bindHandler = function(event_name, handler){

    // 既に登録済みなら古い方を削除
    this.unbindHandler(event_name);

	this.handlers[event_name] = this.handlers[event_name] || [];
	this.handlers[event_name].push(handler);
}

// イベントをアンバインド
BJSocket.prototype.unbindHandler = function(event_name){
    if (event_name in this.handlers)
        delete this.handlers[event_name];
}

//サーバーから送信されたイベントのディスパッチャ
BJSocket.prototype.dispatch = function(event_name, message){

    var chains = this.handlers[event_name];

    if(chains === undefined){
      this.text_callback("caught an unregistered event\nevent_name = " + event_name + "\nmessage = " + message);
      return;
    }

    for(var i=0; i<chains.length; i++){
      chains[0](message);
    }

}

//onload
$(function(){

    print("run bjtimer");

    //socket初期化
    //socket = new BJSocket("ws://127.0.0.1:8000/bjsocket", function(message){
    var start_socket_init = new Date();
	socket = new BJSocket("ws://192.168.11.2:8000/bjsocket", function(message){
	    var messages = $("#text_box").val();
		$("#text_box").val(message + "\n" + messages);
	});
	socket.init();
	print("socket init time : " + (new Date() - start_socket_init));


    //HexGrid初期化
    var start_hex_grid_init = new Date();
    hex_grid = new HexGrid(socket);
	print("hex_grid constructor time : " + (new Date() - start_hex_grid_init));

    //メッセージポップアップの初期化
    HexGridMessage.init();

    //会議室初期化
    bbs_country = new BBSCountry(socket);

    //サーバーから送られてくるエラーのハンドラ
    socket.bindHandler("error", function(message){
        HexGridMessage.open("サーバーエラー", message + "<br>画面を更新して再起動して下さい。")
    });

    //サーバーから送られてくるシステムメッセージのハンドラ
    socket.bindHandler("system", function(message){
        text_callback("システム: " + message)
    });

     //サーバーから送られてくるキャンセルのハンドラ
    socket.bindHandler("cancel", function(message){
        UIEventHandler.createOnCancel(message);
    });

    //サーバにリクエストを送信しヘックスグリッドの初期化開始

	socket.send("init_hexgrid", {});

});