//分頁
$(function () {
    var $table = $('table');
    var $tableB = $('h2');
    var currentPage = 0;//當前頁默認值為0
    var pageSize = 15 ;//每一頁顯示的數目

    $table.bind('paging', function () {
        $table.find('tbody tr').hide().slice(currentPage * pageSize, (currentPage + 1) * pageSize).show();
    });
    var sumRows = $table.find('tbody tr').length;
    var sumPages = Math.ceil(sumRows / pageSize);//總頁數
    var large = sumPages * 36;
    var $pager = $('<div class="page" style="width:' + large + 'px" ></div>');  //新建div，放入a標籤,顯示底部分頁碼
    for (var pageIndex = 0; pageIndex < sumPages; pageIndex++) {
        $('<a href="#thead" id="pageStyle" onclick="changCss(this)"><span>' + (pageIndex + 1) + '</span></a>').bind("click", { "newPage": pageIndex }, function (event) {
            currentPage = event.data["newPage"];
            $table.trigger("paging");

            //觸發分頁函數
        }).appendTo($pager);
        $pager.append(" ");

    }
    $pager.insertAfter($tableB);
    $table.trigger("paging");
    //默認第一頁的a標籤效果
    var $pagess = $('#pageStyle');
    $pagess[0].style.backgroundColor = "rgb(101,129,152)";
    $pagess[0].style.color = "#ffffff";
});

//a鏈接點擊變色，再點其他回覆原色
function changCss(obj) {
    var arr = document.getElementsByTagName("a");
    for (var i = 0; i < arr.length; i++) {
        if (obj == arr[i]) {       //當前頁樣式
            obj.style.backgroundColor = "rgb(101,129,152)";
            obj.style.color = "#ffffff";
        }
        else {
            arr[i].style.color = "";
            arr[i].style.backgroundColor = "";
        }
    }

}