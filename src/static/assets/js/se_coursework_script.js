$(document).ready(function(){ UpdateReady(); });

function UpdateReady()
{
    $('#index_button').click( function(event)
    {
        event.preventDefault();
        LoadPageWithAjax('/account', 'GET', null, 'Главная');
    });

    $('#guide_button').click( function(event)
    {
        event.preventDefault();
        LoadPageWithAjax('/account/guide', 'GET', null, 'Справочник');
    });

    $('#new_work_button').click( function(event)
    {
        event.preventDefault();
        LoadPageWithAjax('/account/new', 'GET', null, 'Новая работа');
    });

    $('#edit_topic_button').click( function(event)
    {
        event.preventDefault();
        LoadPageWithAjax('/account/edit_theme', 'GET', {id: this.name}, 'Выбор темы');
    });

    $('#new_report_button').click( function(event)
    {
        event.preventDefault();
        LoadPageWithAjax('/account/account_add_new_report', 'GET', {id: this.name}, 'Новый отчёт');
    });

    $('.nav').each(function()
    {
        let thesis_id = this.id;
        for (let button of this.children)
        {
            switch (button.name)
            {
                case 'choosing_topic_button':
                    button.onclick = function(event)
                    {
                        event.preventDefault();
                        LoadPageWithAjax('/account/choosing_topic', 'GET', {id: thesis_id}, 'Выбор темы');
                    }
                    break;
                case 'goals_tasks_button':
                    button.onclick = function(event)
                    {
                        event.preventDefault();
                        LoadPageWithAjax('/account/goals_tasks', 'GET', {id: thesis_id}, 'Цели и задачи');
                    }
                    break;
                case 'reports_button':
                    button.onclick = function(event)
                    {
                        event.preventDefault();
                        LoadPageWithAjax('/account/workflow', 'GET', {id: thesis_id}, 'Отчётность');
                    }
                    break;
                case 'preparation_button':
                    button.onclick = function(event)
                    {
                        event.preventDefault();
                        LoadPageWithAjax('/account/preparation_for_defense', 'GET', {id: thesis_id}, 'Подготовка к защите');
                    }
                    break;
                case 'defense_button':
                    button.onclick = function(event)
                    {
                        event.preventDefault();
                        LoadPageWithAjax('/account/defense', 'GET', {id: thesis_id}, 'Защита');
                    }
                    break;
                case 'data_for_practice_button':
                    button.onclick = function(event)
                    {
                        event.preventDefault();
                        LoadPageWithAjax('/account/data_for_practice', 'GET', {id: thesis_id}, 'Настройки');
                    }
                    break;
            }
        }

    });

    $("input[type='file']").each(function()
    {
        $(this).on('change',function()
        {
            var fileName = $(this).val();
            fileName = fileName.replace("C:\\fakepath\\", "");
            $(this).next('label').html(fileName);
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

    let coursework_filter_element = document.getElementById('guide_button');
    if (coursework_filter_element){
        $('[data-toggle="popoverhover"]').popover({ trigger: "hover" });
    }
}

function LoadPageWithAjax(url, typeRequest, dataForRequest, title)
{
    req = $.ajax(
    {
        url: url,
        type: typeRequest,
        data: dataForRequest
    });
    req.done(function(response)
    {
        $('#content').html(response);
        document.title = title;
        let fullUrl = url;
        if (dataForRequest)
        {
            fullUrl += '?';
            for (let parametr in dataForRequest)
            {
                if (fullUrl[fullUrl.length - 1] != '?')
                {
                    fullUrl += '&';
                }
                fullUrl += parametr + '=' + dataForRequest[parametr];
            }
        }
        window.history.pushState({"html":$("#content").html(),"pageTitle":document.title},'', fullUrl);
        UpdateReady();
        feather.replace();
    });

}
