'use strict';

function theses_load() {

    let theses_list = document.getElementById('ThesisList');
    let wt_select = document.getElementById('worktype');
    let page = url.searchParams.get("page");

    let params = new URLSearchParams();
    let wt = wt_select.value;

    // Page first
    if (page && page > 1){
        params.append('page', page);
    }

    if (wt > 1)
    {
        params.append('worktype', wt);
    }

    fetch('fetch_theses?' + params.toString()).then(function(response){

        if (!response.ok){
            window.location.href = '/404.html'
        } else {
            response.text().then(function (text) {
                theses_list.innerHTML = text;
                $('[data-toggle="popoverhover"]').popover({ trigger: "hover" });
            });
        }
    });
}


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

    if (Array.from(params).length){
        window.history.pushState("", "", 'theses.html?' + params.toString());
    } else {
        window.history.pushState("", "", 'theses.html');
    }

    fetch('fetch_theses?' + params.toString()).then(function(response){

        if (!response.ok){
            window.location.href = '/404.html'
        } else {
            response.text().then(function (text) {
                theses_list.innerHTML = text;
                $('[data-toggle="popoverhover"]').popover({ trigger: "hover" });
            });
        }

    });
}

// Select filters
let wt_select = document.getElementById('worktype');

// Get fileters from URI
let url_string = window.location.href
let url = new URL(url_string);
let worktype = url.searchParams.get("worktype");
let page = url.searchParams.get("page");

// Set filter to value from URI
if (worktype && worktype <= wt_select.length && worktype > 0){
    wt_select.value=worktype;
}

// Load theses
theses_load();

// Update theses
wt_select.onchange = theses_update;
