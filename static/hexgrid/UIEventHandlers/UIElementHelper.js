// UIオブジェクトのヘルパー
var UIElementHelper = {};

// ボタンのリスト作成
UIElementHelper.BottonList = function(container){

    // 新規追加するボタンのyオフセット
    this.depth_y = 0;

    // ボタンの最大幅
    this.max_width = 0;

    this.container = new createjs.Container();
    container.addChild(this.container);

}

UIElementHelper.BottonList.prototype = {
    // ボタン追加
    addBtn : function(btnContainer){

        this.container.addChild(btnContainer);
        btnContainer.y = this.depth_y;
        this.depth_y += btnContainer.rectHeight;
    }
}

//  ボタン作成
UIElementHelper.createBotton = function(text){

    // ボタンのコンテナ
    var btnContainer = new createjs.Container();

    // ラベル
    var label = new createjs.Text(text, "20px sans-serif", "White");
    label.x = 5;
    label.y = 5;
    var labelWidth = label.getMeasuredWidth();
    var labelHeight = label.getMeasuredHeight();
    var btn = new createjs.Shape()
    btnContainer.rectHeight = labelHeight + 10;
    btn.graphics.beginFill("Gray").beginStroke("Black").drawRect(0,0, labelWidth+10, btnContainer.rectHeight);
    btnContainer.addChild(btn, label);
    return btnContainer;
}

// テーブル作成
UIElementHelper.Table = function(container){

    this.p_container = container;
    this.container = new createjs.Container();
    this.p_container.addChild(this.container);

    // 行
    this.records = [];

    // テーブルの幅と高さ
    this.width = 0;
    this.height = 0;
}

UIElementHelper.Table.prototype = {

    // 行を追加
    addRecord : function(key, value){
        this.records.push([key, value]);
    },

    // 行を作成
    calc : function(){
        var key_max_width = 0;
        var value_max_width = 0;
        max_height = 0;
        var records_temp = [];

        // keyとvalueの最大幅を更新しながらテキスト生成
        this.records.forEach(function(v){
            var t_key = new createjs.Text(v[0], "20px sans-serif", "Black");
            key_max_width = t_key.getMeasuredWidth() > key_max_width ? t_key.getMeasuredWidth() : key_max_width;
            max_height = t_key.getMeasuredHeight() > max_height ? t_key.getMeasuredHeight() : max_height;
            var t_value = new createjs.Text(v[1], "20px sans-serif", "Black");
            value_max_width = t_value.getMeasuredWidth() > value_max_width ? t_value.getMeasuredWidth() : value_max_width;
            max_height = t_value.getMeasuredHeight() > max_height ? t_value.getMeasuredHeight() : max_height;
            records_temp.push([t_key, t_value]);
        });

        // 日本語だとgetMesuredWidth()とheightがズレるので誤差修正
        max_height += 5;
        key_max_width += 5;
        value_max_width += 5;

        // 最大幅に合わせてレコードを追加
        var current_height_offset = 0;

        print("key_max_width = " + key_max_width);
        print("key_max_height = " + max_height);

        records_temp.forEach(function(v){
            var record_container = new createjs.Container();

            //　罫線作成
            var key_cell = new createjs.Shape();
            key_cell.graphics.beginFill("rgba(255, 255, 255, 1)").beginStroke("Black").drawRect(0,current_height_offset, key_max_width, max_height);
            var value_cell = new createjs.Shape();
            value_cell.graphics.beginFill("rgba(255, 255, 255, 1)").beginStroke("Black").drawRect(key_max_width,current_height_offset, value_max_width, max_height);

            // 文字の位置修正
            v[0].y = current_height_offset;
            v[1].x = key_max_width;
            v[1].y = current_height_offset;

            current_height_offset += max_height;
            this.container.addChild(key_cell, value_cell, v[0], v[1]);
        }.bind(this));

        // テーブルの幅と高さ保存
        this.width = key_max_width + value_max_width;
        this.height = max_height * records_temp.length;

    },

    remove : function(){
        this.p_container.removeChild(this.container);
        delete this.container;
    }


}

// メッセージボックス作成
UIElementHelper.MessageBox = function(p_container, width, height){

    this.width = width;
    this.height = height;

    // テキストコンテナ
    this.container = new createjs.Container();
    p_container.addChild(this.container);

    // 矩形
    this.text_rect_shape = new createjs.Shape();
    var g = this.text_rect_shape.graphics;
    this.cmdFill = g.beginFill("rgba(255, 255, 255, 1)").command;
    this.cmdStroke = g.beginStroke("Black").command;
    this.cmdDrawRect= g.drawRect(0,0, width, height).command;
    this.container.addChild(this.text_rect_shape);

    // テキスト
    this.Text = new createjs.Text("", "20px sans-serif", "Black");
    this.Text.lineWidth = this.width;
    this.container.addChild(this.Text);

}

UIElementHelper.MessageBox.prototype = {

    // テキストをセット、矩形をリサイズ
    setText : function(text){

        // テキストを指定されたピクセル幅で折り返して生成
        var textArray = text.split('');
        var lines = [];
        this.Text.text = "";
        var prevText = "";

        for(var i=0; i<textArray.length; i++){

            this.Text.text += textArray[i];
            if (this.Text.getMeasuredWidth() > this.width){
                lines.push(prevText);
                this.Text.text = textArray[i];
            }

            prevText = this.Text.text;
        }
        lines.push(this.Text.text);
        this.Text.text = lines.join('\n');

        // 矩形リサイズ
        // TODO : getMesuredHeight() > this.heightならthis.heightに合わせてスクロールバー付ける
        this.cmdDrawRect.w = this.width;
        this.cmdDrawRect.h = this.height;

    }
}

