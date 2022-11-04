$(document).ready(function(){ UpdateReady(); });

function UpdateReady()
{
    $('#guide_button').click( function()
    {
        req = $.ajax(
        {
            url: '/account/guide',
            type: 'GET'
        });
        req.done(function(data)
        {
            $('#content').html(data);
            document.title = 'Справочник';
            window.history.pushState({"html":$("#content").html(),"pageTitle":document.title},'', '/account/guide');
            UpdateReady();
        });
    });

    $('#index_button').click( function()
    {
        req = $.ajax(
        {
            url: '/account',
            type: 'GET'
        });
        req.done(function(data)
        {
            $('#content').html(data);
            document.title = 'Главная';
            window.history.pushState({"html":$("#content").html(),"pageTitle":document.title},'', '/account');
            UpdateReady();
        });
    });

    window.onpopstate = function(e)
    {
        if(e.state)
        {
            $("#content").html(e.state.html);
            document.title = e.state.pageTitle;
            UpdateReady();
        }
        else
        {
            location.reload();
        }
    };
}
