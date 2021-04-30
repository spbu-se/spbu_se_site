'use strict';

function theses_load() {

    let theses_list = document.getElementById('ThesisList');
    let wt_select = document.getElementById('worktype');
    let page = url.searchParams.get("page");
    let supervisor_select = document.getElementById('supervisor');
    let startdate_select = document.getElementById('startdate');
    let enddate_select = document.getElementById('enddate');

    let params = new URLSearchParams();
    let wt = wt_select.value;
    let startdate = startdate_select.value;
    let enddate = enddate_select.value;

    // Page first
    if (page && page > 1){
        params.append('page', page);
    }

    // Supervisor?
    if (supervisor_select){
        params.append('supervisor', supervisor_select.value);
    }

    if (wt > 1)
    {
        params.append('worktype', wt);
    }

    params.append('startdate', startdate);
    params.append('enddate', enddate);

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
    let startdate_select = document.getElementById('startdate');
    let enddate_select = document.getElementById('enddate');
    let supervisor_select = document.getElementById('supervisor');

    let params = new URLSearchParams();
    let wt = wt_select.value;

    if (wt > 1)
    {
        params.append('worktype', wt);
    }

    // If supervisor?
    if (supervisor_select){
        params.append('supervisor', supervisor_select.value);
    }

    let startdate = startdate_select.value;
    let enddate = enddate_select.value;

    // End date cannot be less than start date
    if (enddate < startdate){
        enddate = startdate;
        enddate_select.value = startdate_select.value;
    }

    params.append('startdate', startdate);
    params.append('enddate', enddate);

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
let startdate_select = document.getElementById('startdate');
let enddate_select = document.getElementById('enddate');
let supervisor_select = document.getElementById('supervisor');

// Get fileters from URI
let url_string = window.location.href
let url = new URL(url_string);
let worktype = url.searchParams.get("worktype");
let page = url.searchParams.get("page");
let startdate = url.searchParams.get("startdate");
let enddate = url.searchParams.get("enddate");
let supervisor = url.searchParams.get("supervisor");

if (wt_select)
{
    // Set filter to value from URI
    if (worktype && worktype <= wt_select.length && worktype > 0){
        wt_select.value=worktype;
    }

    if (supervisor){

        // Check if this value exist
        if (supervisor_select.innerHTML.indexOf('value="' + supervisor + '"') > -1){
            supervisor_select.value=supervisor;
        } else {
            supervisor_select.value=0;
        }
    }

    if (startdate){
        if (startdate_select.length > 0 && startdate >= startdate_select.options[startdate_select.length - 1].value && startdate <= startdate_select.options[0].value) {
            startdate_select.value=startdate;
        } else {
            startdate_select.value = startdate_select.options[startdate_select.length - 1].value;
        }
    } else {
        startdate_select.value = startdate_select.options[startdate_select.length - 1].value;
    }

    if (enddate){
        if (enddate_select.length > 0 && enddate >= enddate_select.options[enddate_select.length - 1].value && enddate <= enddate_select.options[0].value && enddate >= startdate_select.value) {
            enddate_select.value=enddate;
        } else {
            enddate_select.value = enddate_select.options[0].value;
        }
    } else {
        enddate_select.value = enddate_select.options[0].value;
    }

    // Load theses
    theses_load();

    // Update theses
    wt_select.onchange = theses_update;
    startdate_select.onchange = theses_update;
    enddate_select.onchange = theses_update;
    supervisor_select.onchange = theses_update;
}
