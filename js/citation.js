(function () {
    /**
     * Add all the citations to this object/map
     *
     * Keys can be any valid string, just make sure that the object keys
     * match the [data-citation] attribute value.
     *
     * When you click on any [data-citation] link, an error is logged to
     * the browser console if that key is not found in this object.
     * */
    var citations = {
        'blair2012statistical': `@article{ blair2012statistical,
            title = {Statistical analysis of list experiments},
            author = {Blair, Graeme and Imai, Kosuke},
            journal = {Political Analysis},
            volume = {20},
            number = {1},
            pages = {47--77},
            year = {2012},
            publisher = {Cambridge University Press}
        }`,
        'blair2019motivating': `@article{blair2019motivating,
            title = {Motivating the adoption of new community - minded behaviors: An empirical test in Nigeria},
            author = {Blair, Graeme and Littman, Rebecca and Paluck, Elizabeth Levy},
            journal = {Science advances},
            volume = {5},
            number = {3},
            pages = {eaau5175},
            year = {2019},
            publisher = {American Association for the Advancement of Science}
        }`,
        'lyall2013explaining': `@article{lyall2013explaining,
            title = {Explaining support for combatants during wartime: A survey experiment in Afghanistan},
            author = {Lyall, Jason and Blair, Graeme and Imai, Kosuke},
            journal = {American political science review},
            volume = {107},
            number = {4},
            pages = {679--705},
            year = {2013},
            publisher = {Cambridge University Press}
        }`
    };

    /**
     * Used to keep track of the selected citation
     */
    var current_citation = null;

    var Cite = require('citation-js')

    var $citationModal = $('#citationModal');

    $('body').on('click', 'a[data-citation]', function (e) {
        e.preventDefault();
        var target = e.target;
        var citation_key = target.dataset.citation;
        current_citation = citations[citation_key];
        if (!current_citation) {
            console.error('Missing "' + citation_key + '" citation in the citations object!');
            return false;
        }
        updateCitationModal();
        $citationModal.modal('show');
    });

    $('select', $citationModal).on('change', function () {
        updateCitationModal();
    });

    function updateCitationModal() {
        var options = { generateGraph: false };
        Cite.async(current_citation, options).then(function (result) {
            $('#citation-error').text('');
            updateCitationOutput(result);
        }).catch(function (error) {
            console.log(error)
            $('#citation-error').text(error.message);
        });
    }

    function updateCitationOutput(data) {
        var format = $('#citation-format').val();
        if (format === 'bibliography') {
            $('#fieldset-bibliography').show();
            $('#fieldset-files').hide();
            $('#citation-output').html(data.format(format, {
                template: $('#citation-style').val(),
                lang: 'en-US',
                format: 'html',
            }));
            return;
        }
        $('#fieldset-bibliography').hide();
        $('#fieldset-files').show();

        var type = $('#citation-type').val()
        if (type === 'object') {
            var object = data.format(format, { type: type })
            $('#citation-output').html('<pre>' + JSON.stringify(object, null, 2) + '</pre>')
        } else {
            $('#citation-output').html('<pre>' + data.format(format, {
                type: type
            }) + '</pre>')
        }

        // Highlight
        if (type === 'object' || format === 'data') {
            $('#citation-output pre').attr('data-type', 'json');
            $('#citation-output pre').data('type', 'json');
        } else if (format === 'bibtex' || format === 'biblatex') {
            $('#citation-output pre').attr('data-type', 'bib');
            $('#citation-output pre').data('type', 'bib');
        }
        $('#citation-output pre').highlight();
    }

    /* ------------------------------ Copy Citation ----------------------------- */
    function clipboardFallback(text) {
        /**
         * This function is used if the new clipboard API is not available
         */
        var textarea = document.createElement('textarea');
        textarea.value = text;

        textarea.width = 0;
        textarea.height = 0;

        $('#citation-output').parent()[0].appendChild(textarea);
        textarea.focus();
        textarea.select();

        try {
            var successful = document.execCommand('copy');
            $copyBtn.text(successful ? 'Copied!' : 'Failed!');
        } catch (err) {
            $copyBtn.text('Failed!');
            console.error('Fallback: Oops, unable to copy', err);
        }

        $('#citation-output').parent()[0].removeChild(textarea);

        copy_timeout = setTimeout(function () { $copyBtn.text($copyBtn.data('default-text')); }, 5000);
    }
    var copy_timeout = null;
    var $copyBtn = $('button.copy-citation', $citationModal);
    $copyBtn.data('default-text', $copyBtn.text());
    $copyBtn.on('click', function (e) {
        var copy_text = $('#citation-output').text().trim();
        if (copy_timeout) {
            clearTimeout(copy_timeout);
        }
        if (!navigator.clipboard) {
            clipboardFallback(copy_text);
            return;
        }
        navigator.clipboard.writeText(copy_text).then(function() {
            $copyBtn.text('Copied!');
        }).catch(function (error) {
            $copyBtn.text('Failed!');
        }).finally(function () {
            /* Change back to the original button text after 5 seconds (time in ms) */
            copy_timeout = setTimeout(function () { $copyBtn.text($copyBtn.data('default-text')); }, 5000);
        });
    });
    /* ---------------------------- End Copy Citation --------------------------- */
})();

/* This script is copied from the demo https://citation.js.org/static/js/highlight.js */
/* Code highlighting. Feel free to use, but note it isn't that solid */
jQuery.fn.highlight = function () {
    $(this).each(function () {
        var elm = $(this);
        switch (elm.data('type')) {
            case 'json': case 'js':
                elm.html(elm.text()
                    .replace(/([^\"]*)([\"][^\"]*[\"])([^\"]*)/gi, '$1<span class="string">$2</span>$3')
                    .replace(/([^\']*)([\'][^\']*[\'])([^\']*)/gi, '$1<span class="string">$2</span>$3')
                    .replace(/(function|this|document|for|if|else|var|true|false|throw|return|while|break|typeof|catch|new|undefined|null|class|yield|let|const|switch|break|case|continue|try|delete|in|of)([\s()]+)/g,
                        '<span class="native">$1</span>$2')
                    .replace(/(\w+)(?=\.)/gi, '<span class="object">$1</span>')
                    .replace(/(cite)([(<])/gi, '<span class="important">$1</span>$2')
                    .replace(/(cite)([^\(<])/gi, '<span class="important">$1</span>$2')
                    .replace(/(\w+)(\s*\:)/gi, '<span class="key">$1</span>$2')
                    .replace(/([\s\.{};(])([\w$]+)(?=\s*\()/gi, '$1<span class="function">$2</span>')
                    .replace(/^(.*)(\/\/.*)$/gim, '$1<span class="comment">$2</span>')
                    .replace(/(\/\*[\s\S]*?\*\/)/gi, '<span class="comment">$1</span>')
                    .replace(/(-?(?:\d+\.\d+|\d+\.|\.\d+|\d+)(?:e\d+)?)/gi, '<span class="digit">$1</span>')
                );
                break;
            case 'bib':
                elm.html(elm.text()
                    .replace(/(=\s*)(?:("{)(.*?)(}")|(")(.*?)(")|({{)(.*?)(}})|({)(.*?)(})|(.*?))(?=\s*[,}])/g,
                        function (m, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14) {
                            p1 = p1 || '', p2 = p2 || '', p3 = p3 || '', p4 = p4 || '', p5 = p5 || '', p6 = p6 || '', p7 = p7 || '', p8 = p8 || '',
                                p9 = p9 || '', p10 = p10 || '', p11 = p11 || '', p12 = p12 || '', p13 = p13 || '', p14 = p14 || '';
                            var rgx = /^\d+$/, string = (
                                p3.match(rgx) ||
                                p6.match(rgx) ||
                                p9.match(rgx) ||
                                p12.match(rgx) ||
                                p14.match(rgx)
                            ) ?
                                'digit'
                                :
                                'string';

                            return p1 + p2 + p5 + p8 + p11 + '<span class="' + string + '">' + p3 + p6 + p9 + p12 + p14 + '</span>' + p4 + p7 + p10 + p13
                        })
                    .replace(/(\@)([^\@\{]+)(\{)(\w+)(\,)/gi, '$1<span class="entrytype">$2</span>$3<span class="label">$4</span><span class="default">$5</span>')
                    .replace(/(\w+)\s*(\=)(\s|[^\'\"\w]+)/gi, '<span class="property">$1</span> $2 ')
                );
                break;
            case 'url':
                elm.html(elm.text()
                    .replace(/(https?:\/\/)?((([a-z\d]([a-z\d-]*[a-z\d])*)\.)+[a-z]{2,}|((\d{1,3}\.){3}\d{1,3}))(\:\d+)?((\/[-a-z\d%_.~+:]*)*)(\?[;&a-z\d%_.~+=-]*)?(\#[-a-z\d_]*)?/gi,
                        '<span class="protocol">$1</span>' +
                        '<span class="domain">$2$8</span>' +
                        '<span class="path">$9$12</span>' +
                        '<span class="parameters">$11</span>'
                    )
                )
                break;
            default: return; break;
        }
    });
};
