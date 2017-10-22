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

/*
function MessageBox(text){

}
*/

