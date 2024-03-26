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
        'blair2012statistical': `@article{blair2012statistical,
            title={Statistical analysis of list experiments},
            author={Blair, Graeme and Imai, Kosuke},
            journal={Political Analysis},
            volume={20},
            number={1},
            pages={47--77},
            year={2012},
            publisher={Cambridge University Press}
        }`,
        'blair2013poverty': `@article{blair2013poverty,
            title={Poverty and support for militant politics: Evidence from Pakistan},
            author={Blair, Graeme and Christine Fair, C and Malhotra, Neil and Shapiro, Jacob N},
            journal={American Journal of Political Science},
            volume={57},
            number={1},
            pages={30--48},
            year={2013},
            publisher={Blackwell Publishing Inc Malden, USA}
        }`,
        'blair2010list': `@article{blair2010list,
            title={list: Statistical methods for the item count technique and list experiment},
            author={Blair, Graeme and Imai, Kosuke},
            journal={The Comprehensive R Archive Network (CRAN)},
            year={2010}
        }`,
        'lyall2013explaining': `@article{lyall2013explaining,
            title={Explaining support for combatants during wartime: A survey experiment in Afghanistan},
            author={Lyall, Jason and Blair, Graeme and Imai, Kosuke},
            journal={American Political Science Review},
            volume={107},
            number={4},
            pages={679--705},
            year={2013},
            publisher={Cambridge University Press}
        }`,
        'blair2014comparing': `@article{blair2014comparing,
            title={Comparing and combining list and endorsement experiments: Evidence from Afghanistan},
            author={Blair, Graeme and Imai, Kosuke and Lyall, Jason},
            journal={American Journal of Political Science},
            volume={58},
            number={4},
            pages={1043--1063},
            year={2014}
        }`,
        'blair2015design': `@article{blair2015design,
            title={Design and analysis of the randomized response technique},
            author={Blair, Graeme and Imai, Kosuke and Zhou, Yang-Yang},
            journal={Journal of the American Statistical Association},
            volume={110},
            number={511},
            pages={1304--1319},
            year={2015}
        }`,
        'blair2015rr': `@misc{blair2015rr,
            title={rr: Statistical methods for the randomized response technique},
            author={Blair, Graeme and Zhou, Yang-Yang and Imai, Kosuke},
            journal={The Comprehensive R Archive Network (CRAN)},
            year={2015}
        }`,
        'blair2015survey': `@article{blair2015survey,
            title={Survey methods for sensitive topics},
            author={Blair, Graeme},
            journal={Comparative Politics Newsletter},
            volume={12},
            pages={44},
            year={2015}
        }`,
        'blair2019motivating': `@article{blair2019motivating,
            title={Motivating the adoption of new community-minded behaviors: An empirical test in Nigeria},
            author={Blair, Graeme and Littman, Rebecca and Paluck, Elizabeth Levy},
            journal={Science Advances},
            volume={5},
            number={3},
            year={2019}
        }`,
        'gomila2017audio': `@article{gomila2017audio,
            title={The audio check: A method for improving data quality and detecting data fabrication},
            author={Gomila, Robin and Littman, Rebecca and Blair, Graeme and Paluck, Elizabeth Levy},
            journal={Social Psychological and Personality Science},
            volume={8},
            number={4},
            year={2017},
            publisher={SAGE Publications}
        }`,
        'blair2019list': `@article{blair2019list,
            title={List experiments with measurement error},
            author={Blair, Graeme and Chou, Winston and Imai, Kosuke},
            journal={Political Analysis},
            volume={27},
            number={4},
            pages={455--480},
            year={2019}
        }`,
        'blair2019declaring': `@article{blair2019declaring,
            title={Declaring and diagnosing research designs},
            author={Blair, Graeme and Cooper, Jasper and Coppock, Alexander and Humphreys, Macartan},
            journal={American Political Science Review},
            volume={113},
            number={3},
            pages={838--859},
            year={2019}
        }`,
        'blair2020worry': `@article{blair2020worry,
            title={When to worry about sensitivity bias: A social reference theory and evidence from 30 years of list experiments},
            author={Blair, Graeme and Coppock, Alexander and Moor, Margaret},
            journal={American Political Science Review},
            year={2020}
        }`,
        'blair2013policy': `@article{blair2013policy,
            title={Where policy experiments are conducted in economics and political science: The missing autocracies},
            author={Blair, Graeme and Iyengar, Radha K. and Shapiro, Jacob N.},
            year={2013}
        }`,
        'blair2016declaredesign': `@article{blair2016declaredesign,
            title={DeclareDesign},
            author={Blair, Graeme and Cooper, Jasper and Coppock, Alexander and Humphreys, Macartan},
            journal={Software package for R, available at http://declaredesign.org},
            year={2016}
        }`,
        'blair2018estimatr': `@article{blair2018estimatr,
            title={estimatr: Fast estimators for design-based inference},
            author={Blair, Graeme and Cooper, Jasper and Coppock, Alexander and Humphreys, Macartan and Sonnet, Luke and Fultz, Neal},
            year={2018}
        }`,
        'blair2022does': `@article{blair2022does,
            title={How does armed conflict shape investment? Evidence from the mining sector},
            author={Blair, Graeme and Christensen, Darin and Wirtschafter, Valerie},
            journal={Journal of Politics},
            year={2022}
        }`,
        'blair2021commodity': `@article{blair2021commodity,
            title={Do commodity price shocks cause armed conflict? A meta-analysis of natural experiments},
            author={Blair, Graeme and Christensen, Darin and Rudkin, Aaron},
            journal={American Political Science Review},
            number={Forthcoming},
            year={2021}
        }`,
        'blair2021conducting': `@article{blair2021conducting,
            title={Conducting experiments in multiple contexts},
            author={Blair, Graeme and McClendon, Gwyneth},
            journal={Advances in experimental political science},
            pages={411--428},
            year={2021},
            publisher={Cambridge University Press New York}
        }`,
        'blair2021trusted': `@article{blair2021trusted,
            title={Trusted authorities can change minds and shift norms during conflict.},
            author={Blair, Graeme and Littman, Rebecca and Nugent, Elizabeth and Wolfe, Rebecca and Bukar, Mohammed and Crisman, Benjamin and Etim, Anthony and Hazlett, Chad and Kim, Jiyoung},
            journal={Proceedings of the National Academy of Sciences},
            year={2021}
        }`,
        'blair2021community': `@article{blair2021community,
            title={Community policing does not build citizen trust in police or reduce crime in the Global South},
            author={Blair, Graeme and Weinstein, Jeremy M and Christia, Fotini and Arias, Eric and Badran, Emile and Blair, Robert A and Cheema, Ali and Farooqui, Ahsan and Fetzer, Thiemo and Grossman, Guy and others},
            journal={Science},
            volume={374},
            number={6571},
            pages={eabd3446},
            year={2021},
            publisher={American Association for the Advancement of Science}
        }`,
        'blair2018fabricatr': `@article{blair2018fabricatr,
            title={fabricatr: Imagine your data before you collect It},
            author={Blair, Graeme and Cooper, Jasper Jack and Coppock, Alex and Humphreys, Macartan and Rudkin, A and Fultz, N},
            year={2018}
        }`,
        'herman2022field': `@article{herman2022field,
            title={Field Experiments in the Global South: Assessing Risks, Localizing Benefits, and Addressing Positionality},
            author={Herman, Biz and Panin, Amma and Wellman, Elizabeth Iams and Blair, Graeme and Pruett, Lindsey D and Ochieng’Opalo, Ken and Alarian, Hannah M and Grossman, Allison N and Tan, Yvonne and Dyzenhaus, Alex P and others},
            journal={PS: Political Science \& Politics},
            pages={1--1},
            year={2022},
            publisher={Cambridge University Press}
        }`,
        'blair2022accessing': `@article{blair2022accessing,
            title={Accessing justice for survivors of violence against women},
            author={Blair, Graeme and Jassal, Nirvikar},
            journal={Science},
            volume={377},
            number={6602},
            pages={150--151},
            year={2022},
            publisher={American Association for the Advancement of Science}
        }`,
        'blair2022point': `@article{blair2022point,
            title={The Point of Attack: Where and Why Does Oil Cause Armed Conflict in Africa?},
            author={Blair, Graeme and Christensen, Darin and Gibilisco, Michael},
            journal={Working Paper},
            year={2022},
            publisher={California Institute of Technology Pasadena}
        }`,
        'blair2023research': `@incollection{blair2023research,
            title={Research Design in the Social Sciences},
            author={Blair, Graeme and Coppock, Alexander and Humphreys, Macartan},
            year={2023},
            publisher={Princeton University Press}
        }`,
        'littman2023evidence': `@article{littman2023evidence,
            title={Evidence required for ethical social science},
            author={Littman, Rebecca and Wolfe, Rebecca and Blair, Graeme and Ryan, Sarah},
            journal={Science},
            volume={379},
            number={6629},
            pages={247--247},
            year={2023},
            publisher={American Association for the Advancement of Science}
        }`,
    };

    /**
     * Used to keep track of the selected citation
     */
    var current_citation = null;

    var Cite = require('citation-js')

    var citationModalEl = document.querySelector('#citationModal');
    var citationModal = new bootstrap.Modal(citationModalEl);

    var citationOutput = document.querySelector('#citation-output');

    document.body.addEventListener('click', function (e) {
        var citationAnchor = e.target.closest('a[data-citation]');
        if (!citationAnchor) {
            return;
        }
        e.preventDefault();
        var citation_key = citationAnchor.dataset.citation;
        current_citation = citations[citation_key];
        if (!current_citation) {
            console.error('Missing "' + citation_key + '" citation in the citations object!');
            return false;
        }
        updateCitationModal();
        citationModal.show();
    });

    citationModalEl.addEventListener('change', function () {
        updateCitationModal();
    });

    function updateCitationModal() {
        var options = { generateGraph: false };
        var citationError = document.querySelector('#citation-error');
        Cite.async(current_citation, options).then(function (result) {
            citationError.textContent = '';
            updateCitationOutput(result);
        }).catch(function (error) {
            console.log(error);
            citationError.textContent = error.message;
        });
    }

    function updateCitationOutput(data) {
        var format = document.querySelector('#citation-format').value;
        var bibliographyFieldset = document.querySelector('#fieldset-bibliography')
        if (format === 'bibliography') {
            bibliographyFieldset.style.display = '';
            citationOutput.innerHTML = (data.format(format, {
                template: document.querySelector('#citation-style').value,
                lang: 'en-US',
                format: 'html',
            }));
            return;
        }
        bibliographyFieldset.style.display = 'none';

        var type = 'text';
        if (type === 'object') {
            var object = data.format(format, { type: type })
            citationOutput.innerHTML = ('<pre>' + JSON.stringify(object, null, 2) + '</pre>');
        } else {
            citationOutput.innerHTML = ('<pre>' + data.format(format, {
                type: type
            }) + '</pre>');
        }

        // Highlight
        var output = citationOutput.querySelectorAll('pre');
        if (output) {
            output.forEach(function (pre) {
                if (type === 'object' || format === 'data') {
                    pre.dataset.type = 'json';
                } else if (format === 'bibtex' || format === 'biblatex') {
                    pre.dataset.type = 'bib';
                }
            });
        }
        highlight(output);
    }

    /* ------------------------------ Copy Citation ----------------------------- */
    var copy_timeout = null;
    var copyBtnEl = citationModalEl.querySelector('button.copy-citation');
    copyBtnEl.dataset.defaultText = copyBtnEl.textContent
    copyBtnEl.addEventListener('click', function (e) {
        var copy_text = citationOutput.textContent.trim();
        if (copy_timeout) {
            clearTimeout(copy_timeout);
        }
        if (!navigator.clipboard) {
            clipboardFallback(copy_text);
            return;
        }
        navigator.clipboard.writeText(copy_text).then(function () {
            copyBtnEl.textContent = 'Copied!';
        }).catch(function (error) {
            copyBtnEl.textContent = 'Failed!';
        }).finally(function () {
            /* Change back to the original button text after 5 seconds (time in ms) */
            copy_timeout = setTimeout(function () { copyBtnEl.textContent = copyBtnEl.dataset.defaultText; }, 5000);
        });
    });
    function clipboardFallback(text) {
        /**
         * This function is used if the new clipboard API is not available
         */
        var textarea = document.createElement('textarea');
        textarea.value = text;

        textarea.width = 0;
        textarea.height = 0;

        citationOutput.parentElement.appendChild(textarea);
        textarea.focus();
        textarea.select();

        try {
            var successful = document.execCommand('copy');
            copyBtnEl.text(successful ? 'Copied!' : 'Failed!');
        } catch (err) {
            copyBtnEl.text('Failed!');
            console.error('Fallback: Oops, unable to copy', err);
        }

        citationOutput.parentElement.removeChild(textarea);

        copy_timeout = setTimeout(function () { copyBtnEl.textContent = copyBtnEl.dataset.defaultText; }, 5000);
    }
    /* ---------------------------- End Copy Citation --------------------------- */

    /* ----------------- Highlight code modified for Vanilla JS ----------------- */
    function highlight(elements) {
        if (!elements) {
            return;
        }
        elements.forEach(function (el) {
            if (!el.dataset.type) {
                return;
            }
            switch (el.dataset.type) {
                case 'json': case 'js':
                    el.innerHTML = (el.textContent
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
                    el.innerHTML = (el.textContent
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
                    el.innerHTML = (el.textContent
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
    }
    /* --------------- End Highlight code modified for Vanilla JS --------------- */
})();
