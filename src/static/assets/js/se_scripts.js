'use strict';

function theses_load() {

    let theses_list = document.getElementById('ThesisList');
    let wt_select = document.getElementById('worktype');
    let page = url.searchParams.get("page");
    let supervisor_select = document.getElementById('supervisor');
    let course_select = document.getElementById('course');
    let startdate_select = document.getElementById('startdate');
    let enddate_select = document.getElementById('enddate');
    let search_field = document.getElementById('thesis_search_field');

    let params = new URLSearchParams();
    let wt = wt_select.value;
    let startdate = startdate_select.value;
    let enddate = enddate_select.value;

    // Page first
    if (page && page > 1){
        params.append('page', page);
    }

    if (search_field)
    {
        params.append('search', search_field.value);
    }

    // Supervisor?
    if (supervisor_select){
        params.append('supervisor', supervisor_select.value);
    }

    // Course?
    if (course_select){
        params.append('course', course_select.value);
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
    let course_select = document.getElementById('course');
    let search_field = document.getElementById('thesis_search_field');

    let params = new URLSearchParams();
    let wt = wt_select.value;

    if (search_field)
    {
        params.append('search', search_field.value);
    }

    if (wt > 1)
    {
        params.append('worktype', wt);
    }

    // If supervisor?
    if (supervisor_select){
        params.append('supervisor', supervisor_select.value);
    }

    // If course?
    if (course_select){
        params.append('course', course_select.value);
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

//
// Search thesis by click button
//
function search_thesis()
{
    let theses_list = document.getElementById('ThesisList');
    let params = new URLSearchParams();

    // Text
    if (search_field){
        params.append('search', search_field.value);
    }

    // Clear filters
    wt_select.value=0;
    supervisor_select.value=0;
    course_select.value=0;
    startdate_select.value = startdate_select.options[startdate_select.length - 1].value;
    enddate_select.value = enddate_select.options[0].value;

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


// Find search field
let search_field = document.getElementById('thesis_search_field');
let search_button = document.getElementById('thesis_search_button');

// Select filters
let wt_select = document.getElementById('worktype');
let startdate_select = document.getElementById('startdate');
let enddate_select = document.getElementById('enddate');
let supervisor_select = document.getElementById('supervisor');
let course_select = document.getElementById('course');

// Get fileters from URI
let url_string = window.location.href
let url = new URL(url_string);
let worktype = url.searchParams.get("worktype");
let page = url.searchParams.get("page");
let startdate = url.searchParams.get("startdate");
let enddate = url.searchParams.get("enddate");
let supervisor = url.searchParams.get("supervisor");
let course = url.searchParams.get("course");
let search = url.searchParams.get("search");

if (search_field && search_button)
{
    search_button.onclick = search_thesis;

    search_field.addEventListener("keyup", function(event) {
        // Number 13 is the "Enter" key on the keyboard
        if (event.keyCode === 13) {
            // Cancel the default action, if needed
            event.preventDefault();
            // Trigger the button element with a click
            search_button.click();
        }
    });
}

if (wt_select)
{

    // Set filter to value from URI
    if (wt_select.innerHTML.indexOf('value="' + worktype + '"') > -1){
        console.log(worktype);
        wt_select.value=worktype;
    } else {
        wt_select.value=0;
    }

    if (search){
        search_field.value=search;
    }

    if (supervisor){

        // Check if this value exist
        if (supervisor_select.innerHTML.indexOf('value="' + supervisor + '"') > -1){
            supervisor_select.value=supervisor;
        } else {
            supervisor_select.value=0;
        }
    }

    if (course){
        if (course_select.innerHTML.indexOf('value="' + course + '"') > -1){
            course_select.value=course;
        } else {
            course_select.value=0;
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
    course_select.onchange = theses_update;
}


function themes_load() {

    let themes_list = document.getElementById('ThemesList');

    let themes_level_select = document.getElementById('level');
    let themes_supervisor_select = document.getElementById('supervisor');
    let themes_company_select = document.getElementById('company');

    let page = url.searchParams.get("page");

    let params = new URLSearchParams();

    // Page first
    if (page && page > 1){
        params.append('page', page);
    }

    // Supervisor?
    if (themes_supervisor_select){
        params.append('supervisor', themes_supervisor_select.value);
    }

    // level?
    if (themes_level_select){
        params.append('level', themes_level_select.value);
    }

    if (themes_company_select)
    {
        params.append('company', themes_company_select.value);
    }

    fetch('fetch_themes?' + params.toString()).then(function(response){

        if (!response.ok){
            window.location.href = '/404.html'
        } else {
            response.text().then(function (text) {
                themes_list.innerHTML = text;
            });
        }
    });
}


function themes_update() {

    let themes_list = document.getElementById('ThemesList');

    let themes_level_select = document.getElementById('level');
    let themes_supervisor_select = document.getElementById('supervisor');
    let themes_company_select = document.getElementById('company');

    let page = url.searchParams.get("page");

    let params = new URLSearchParams();

    // Page first
    if (page && page > 1){
        params.append('page', page);
    }

    // Supervisor?
    if (themes_supervisor_select){
        params.append('supervisor', themes_supervisor_select.value);
    }

    // level?
    if (themes_level_select){
        params.append('level', themes_level_select.value);
    }

    if (themes_company_select)
    {
        params.append('company', themes_company_select.value);
    }

    fetch('fetch_themes?' + params.toString()).then(function(response){

        if (!response.ok){
            window.location.href = '/404.html'
        } else {
            response.text().then(function (text) {
                themes_list.innerHTML = text;
            });
        }
    });
}


function diploma_themes_filter()
{
    // Select filters
    let themes_level_select = document.getElementById('level');
    let themes_supervisor_select = document.getElementById('supervisor');
    let themes_company_select = document.getElementById('company');

    // Get fileters from URI
    let url_string = window.location.href
    let url = new URL(url_string);

    let level = url.searchParams.get("level");
    let page = url.searchParams.get("page");
    let supervisor = url.searchParams.get("supervisor");
    let company = url.searchParams.get("company");

    if (themes_level_select)
    {

        // Set filter to value from URI
        if (level > 0){
            if (themes_level_select.innerHTML.indexOf('value="' + level + '"') > -1){
                themes_level_select.value=level;
            }
        } else {
            themes_level_select.value=0;
        }

        if (supervisor > 0){
            if (themes_supervisor_select.innerHTML.indexOf('value="' + supervisor + '"') > -1){
                themes_supervisor_select.value=supervisor;
            }
        } else {
            themes_supervisor_select.value=0;
        }

        if (company > 0){
            if (themes_company_select_select.innerHTML.indexOf('value="' + company + '"') > -1){
                themes_company_select_select.value=course;
            }
        } else {
            themes_supervisor_select.value=0;
        }
    }

    // Load themes
    themes_load();

    // Update themes
    themes_level_select.onchange = themes_update;
    themes_supervisor_select.onchange = themes_update;
    themes_company_select.onchange = themes_update;
}

// This is Diploma Themes ?
let diploma_themes_filter_element = document.getElementById('DiplomaThemesFilter');

if (diploma_themes_filter_element){
    diploma_themes_filter();
}