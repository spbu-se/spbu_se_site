'use strict';

//
// Update theses list
//

function theses_update() {

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

// Select filters
let wt_select = document.getElementById('worktype');

// Get fileters from URI
var url_string = window.location.href
var url = new URL(url_string);
var worktype = url.searchParams.get("worktype");

// Set filter to value from URI
if (worktype && worktype <= wt_select.length && worktype > 0){
    wt_select.value=worktype
}

// Update theses
theses_update();
wt_select.onchange = theses_update;
