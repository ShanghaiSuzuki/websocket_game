HexGridMessage = {}

HexGridMessage.init = function(){
    var inst = $('[data-remodal-id=modal]').remodal();

    $(document).on("closed", ".remodal", function(e){

        if(HexGridMessage.handler && e.reason == "confirmation"){
            HexGridMessage.handler();
        }
        /*
        $(".remodal-is-closed").remove();
        $("<div data-remodal-id=modal></div>").append(
            $("<h1 id=\"modal_title\"></h1>")
        ).append(
            $("<p id=\"modal_message\"></p>")
        ).append(
            $("<br>")
        ).append(
            $("<button data-remodal-action=\"confirm\" class=\"remodal-confirm\" id=\"remodal_ok_button\">OK</button>")
        ).append(
            $("<button data-remodal-action=\"cancel\" class=\"remodal-cancel\" id=\"remodal_cancel_button\">CANCEL</button>")
        ).appendTo($(document.body));
        */
        print("HexGridMessage.onClose colled");
    });
}

//メッセージをポップアップ
//confirmとハンドラを渡さないとconfirmボタンのみの確認用ポップアップになる
HexGridMessage.open = function(title, message, confirm_handler){

   //ポップアップの中身を変更
    $("#modal_title").html(title);
    $("#modal_message").html(message);

    //ハンドラがあれば登録
    if(confirm_handler){
        HexGridMessage.handler = confirm_handler;
        $("#remodal_cancel_button").show();
        print("HexGridMesage.open with handle");
    }
    //なければ承認ボタンのみ
    else{
        HexGridMessage.handler = undefined;
        $("#remodal_cancel_button").hide();
        print("HexGridMessage.open with no handle");
    }

    var inst = $('[data-remodal-id=modal]').remodal();
    inst.open();
}


