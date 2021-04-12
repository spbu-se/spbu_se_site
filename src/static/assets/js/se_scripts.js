'use strict';

//
// Update theses list
//

function update() {

    let theses_list = document.getElementById('ThesisList');
    let wt_select = document.getElementById('worktype');

    let params = new URLSearchParams();
    let wt = wt_select.value;
    if (wt > 1)
    {
        params.append('worktype', wt);
    }

    fetch('fetch_theses?' + params.toString()).then(function(response){
        response.text().then(function (text) {
            theses_list.innerHTML = text;
            $('[data-toggle="popoverhover"]').popover({ trigger: "hover" });
        });
    });
}

// Toggle popover on hover
$('[data-toggle="popoverhover"]').popover({ trigger: "hover" });

let wt_select = document.getElementById('worktype');
wt_select.onchange = update;
