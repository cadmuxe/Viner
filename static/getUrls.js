
function getUrls(){
    var plist =$($('div#main div.tpc_content')[0]).find('input');
    var urls=[];
    for(var i=0; i < plist.length; i++){
        urls.push(plist[i].src);
    }
    return urls;
}