function save(data){
    var datas = JSON.stringify(data);
    window.frames["f%s"].save(datas);
}

function save1024(){
    f = document.createElement('iframe');
    f.setAttribute('name', 'f%s');
    f.setAttribute('allowtransparency', 'true');
    f.setAttribute('style', 'border: 0; width: 1px; height: 1px; position: absolute; left: 0; top: 0;');
    document.body.appendChild(f);
    window.frames['f%s'].document.write(
        '<html><body style=""background-color:transparent;">' +
        '<form action="http://localhost:5000/api/saver" method="post" id="form" accept-charset="utf-8">' +
        '<input type="hidden" name="data" id="data" value="">' +
        '</form>' +
        "<scr" + "ipt>function save(datas){var i = document.getElementById('data');" +
        "var f=document.getElementById('form'); i.value=datas; f.submit();}" +
        "</scr" + "ipt></body></html>"
    );
}
function run(){
    data = {"website":document.location.hostname,
            "title":document.title,
            "urls":getUrls()};
    save1024();
    save(data);
}
run();
