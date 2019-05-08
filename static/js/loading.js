//loading
//取瀏覽器的高度和寬度
var _PageHeight = document.documentElement.clientHeight,
    _PageWidth = document.documentElement.clientWidth;
//計算loading框距離頂部和左部的距離（loading框的寬度為215px，高度為61px）
var _LoadingTop = _PageHeight > 61 ? (_PageHeight - 61) / 2 : 0,
    _LoadingLeft = _PageWidth > 215 ? (_PageWidth - 215) / 2 : 0;
//在頁面未加載完畢之前顯示的loading Html自定義內容
var _LoadingHtml = '<div id="loadingDiv" class="loadDiv" style="height:' + _PageHeight + 'px;top:0;"><div class="load" style="left: ' + _LoadingLeft + 'px; top:' + _LoadingTop + 'px; "><img src="static/loading2.gif" style="height:25px;vertical-align:sub;">搜尋中，請稍後...</div></div>';
//呈現loading效果
document.write(_LoadingHtml);



//監聽加載狀態改變
document.onreadystatechange = completeLoading;
//加載狀態為complete時移除loading效果
function completeLoading() {
    if (document.readyState == "complete") {
        var loadingMask = document.getElementById('loadingDiv');
        loadingMask.parentNode.removeChild(loadingMask);
    }
}