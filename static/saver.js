
function getUrls(){
    var plist =$($('div#main div.tpc_content')[0]).find('input');
    var urls=[];
    for(var i=0; i < plist.length; i++){
        urls.push(plist[i].src);
    }
}

function save(data){
    var datas = JSON.stringify(data);
    window.frames["postframe"].save(datas);
}

function save1024(){
    f = document.createElement('iframe');
    f.setAttribute('name', 'postframe');
    f.setAttribute('allowtransparency', 'true');
    f.setAttribute('style', 'border: 0; width: 1px; height: 1px; position: absolute; left: 0; top: 0;');
    document.body.appendChild(f);
    window.frames['postframe'].document.write(
    '<html><body style=""background-color:transparent;">' +
    '<form action="http://localhost:5000/api/saver" method="post" id="form" accept-charset="utf-8">' +
    '<input type="hidden" name="data" id="data" value="">' +
    '</form>' +
    "<scr" + "ipt>function save(datas){var i = document.getElementById('data');" +
    "var f=document.getElementById('form'); i.value=datas; f.submit();}" +
    "</scr" + "ipt></body></html>"
    );
}
