/* Data Contributor questionnaire. One page: steps are shown and hidden here.
   There is no submit yet. */
(function ($) {
    var ISO_ALPHA2 = [
        "AD", "AE", "AF", "AG", "AI", "AL", "AM", "AO", "AR", "AS", "AT", "AU", "AW", "AX", "AZ",
        "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BL", "BM", "BN", "BO", "BQ", "BR",
        "BS", "BT", "BW", "BY", "BZ", "CA", "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL", "CM",
        "CN", "CO", "CR", "CU", "CV", "CW", "CX", "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ",
        "EC", "EE", "EG", "ER", "ES", "ET", "FI", "FJ", "FK", "FM", "FO", "FR", "GA", "GB", "GD",
        "GE", "GF", "GG", "GH", "GI", "GL", "GM", "GN", "GP", "GQ", "GR", "GS", "GT", "GU", "GW",
        "GY", "HK", "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IM", "IN", "IQ", "IR", "IS", "IT",
        "JE", "JM", "JO", "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ",
        "LA", "LB", "LC", "LI", "LK", "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MC", "MD", "ME",
        "MF", "MG", "MH", "MK", "ML", "MM", "MN", "MO", "MP", "MQ", "MR", "MS", "MT", "MU", "MV",
        "MW", "MX", "MY", "MZ", "NA", "NC", "NE", "NF", "NG", "NI", "NL", "NO", "NP", "NR", "NU",
        "NZ", "OM", "PA", "PE", "PF", "PG", "PH", "PK", "PL", "PM", "PN", "PR", "PS", "PT", "PW",
        "PY", "QA", "RE", "RO", "RS", "RU", "RW", "SA", "SB", "SC", "SD", "SE", "SG", "SH", "SI",
        "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "SS", "ST", "SV", "SX", "SY", "SZ", "TC", "TD",
        "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO", "TR", "TT", "TV", "TW", "TZ", "UA", "UG",
        "US", "UY", "UZ", "VA", "VC", "VE", "VG", "VI", "VN", "VU", "WF", "WS", "XK", "YE", "YT",
        "ZA", "ZM", "ZW"
    ];

    function fillPlaces(select) {
        var names = new Intl.DisplayNames(["en"], { type: "region" });
        var places = ISO_ALPHA2.map(function (code) {
            var label;
            try {
                label = names.of(code);
            } catch (error) {
                return null;
            }
            if (!label || label === code) {
                return null;
            }
            return { value: code, label: label };
        }).filter(Boolean);

        places.sort(function (a, b) {
            return a.label.localeCompare(b.label, "en");
        });

        [
            { value: "CH", label: "Switzerland" },
            { value: "EU", label: "European Union" }
        ].forEach(function (place) {
            var option = document.createElement("option");
            option.value = place.value;
            option.textContent = place.label;
            select.appendChild(option);
        });

        places.forEach(function (place) {
            if (place.value === "CH") {
                return;
            }
            var option = document.createElement("option");
            option.value = place.value;
            option.textContent = place.label;
            select.appendChild(option);
        });
    }

    function bindStep(prefix) {
        var $none = $("#" + prefix + "-none");
        var $purpose = $("#" + prefix + "-purpose");
        var $date = $("#" + prefix + "-date");
        var $place = $("#" + prefix + "-place");
        var restrictions = [$purpose, $date, $place];
        var purposePanel = "#" + prefix + "-purpose-panel";
        var datePanel = "#" + prefix + "-date-panel";
        var placePanel = "#" + prefix + "-place-panel";

        function clearPurposes() {
            $(purposePanel + " input:enabled").prop("checked", false);
        }

        function clearDateValue() {
            var $dateInput = $("#" + prefix + "-from-date");
            if ($date.prop("disabled")) {
                return;
            }
            $dateInput.val("");
        }

        function clearPlaceValue() {
            var $placeSelect = $("#" + prefix + "-place-select");
            if ($place.prop("disabled")) {
                return;
            }
            $placeSelect.val("");
        }

        fillPlaces(document.getElementById(prefix + "-place-select"));

        $none.on("change", function () {
            if (!this.checked) {
                return;
            }
            restrictions.forEach(function ($box) {
                if (!$box.prop("disabled")) {
                    $box.prop("checked", false);
                }
            });
            showPanel(purposePanel, false, clearPurposes);
            showPanel(datePanel, false, clearDateValue);
            showPanel(placePanel, false, clearPlaceValue);
        });

        $purpose.on("change", function () {
            if (this.checked) {
                $none.prop("checked", false);
            }
            showPanel(purposePanel, this.checked, this.checked ? null : clearPurposes);
        });

        $date.on("change", function () {
            if (this.checked) {
                $none.prop("checked", false);
            }
            showPanel(datePanel, this.checked, this.checked ? null : clearDateValue);
        });

        $place.on("change", function () {
            if (this.checked) {
                $none.prop("checked", false);
            }
            showPanel(placePanel, this.checked, this.checked ? null : clearPlaceValue);
        });

        $("#" + prefix + "-from-date").on("change", function () {
            if (this.min && this.value && this.value < this.min) {
                this.value = "";
            }
        });

        $("#step-" + prefix).on("change", "input, select", function () {
            resetFollowing(prefix);
            var $error = $("#step-" + prefix + " .q-step-error");
            if ($error.length && !$error.prop("hidden")) {
                showStepError(prefix, missingAnswers(prefix));
            }
        });
    }

    /* These four action questions only. Each may only narrow the previous one,
       and editing one clears the later ones in this list. Questions after the
       fourth are not in this list and must not be cleared by these edits.
       Still to add: distribution, then sharing modifications. */
    var ACTION_STEPS = ["access", "reproduce"];

    function dayAfter(isoDate) {
        var parts = isoDate.split("-");
        var date = new Date(Date.UTC(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2])));
        date.setUTCDate(date.getUTCDate() + 1);
        return date.toISOString().slice(0, 10);
    }

    function formatIsoDate(isoDate) {
        var parts = isoDate.split("-");
        var date = new Date(Date.UTC(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2])));
        return new Intl.DateTimeFormat("en", {
            day: "numeric",
            month: "short",
            year: "numeric",
            timeZone: "UTC"
        }).format(date);
    }

    function lockChecked($input) {
        $input.prop("checked", true).prop("disabled", true);
        $input.closest(".q-option").addClass("is-locked");
        $("<input>", {
            type: "hidden",
            class: "q-lock-mirror",
            name: $input.attr("name"),
            value: $input.val(),
            "data-step": $input.closest("section").attr("id")
        }).appendTo("#contributor-questionnaire");
    }

    function lockOff($input) {
        $input.prop("checked", false).prop("disabled", true);
        $input.closest(".q-option").addClass("is-locked");
    }

    function showLockedPanel(panel) {
        var $panel = $(panel);
        $panel.stop(true, true);
        clearPanelMotion($panel);
        $panel.prop("hidden", false);
    }

    function releaseStep(prefix) {
        var $step = $("#step-" + prefix);
        $step.find(".is-locked").removeClass("is-locked");
        $step.find("input, select").prop("disabled", false);
        $("#" + prefix + "-from-date").removeAttr("min");
        $step.find(".q-date-hint").prop("hidden", true);
        $("#contributor-questionnaire .q-lock-mirror").filter(function () {
            return $(this).data("step") === "step-" + prefix;
        }).remove();
    }

    function syncFromPrevious(prefix) {
        var index = ACTION_STEPS.indexOf(prefix);
        if (index <= 0) {
            return;
        }
        var previous = ACTION_STEPS[index - 1];
        releaseStep(prefix);

        var previousRestricted = $("#" + previous + "-purpose").prop("checked")
            || $("#" + previous + "-date").prop("checked")
            || $("#" + previous + "-place").prop("checked");

        if (previousRestricted) {
            lockOff($("#" + prefix + "-none"));
        }

        var keptPurposes = $("#" + previous + "-purpose-panel input:checked").map(function () {
            return this.value;
        }).get();
        if (keptPurposes.length) {
            lockChecked($("#" + prefix + "-purpose"));
            showLockedPanel("#" + prefix + "-purpose-panel");
            $("#" + prefix + "-purpose-panel input").each(function () {
                if (keptPurposes.indexOf(this.value) !== -1) {
                    lockChecked($(this));
                }
            });
        }

        if ($("#" + previous + "-place").prop("checked")) {
            var place = $("#" + previous + "-place-select").val();
            if (place) {
                lockChecked($("#" + prefix + "-place"));
                showLockedPanel("#" + prefix + "-place-panel");
                var $placeSelect = $("#" + prefix + "-place-select");
                $placeSelect.val(place).prop("disabled", true);
                $("<input>", {
                    type: "hidden",
                    class: "q-lock-mirror",
                    name: $placeSelect.attr("name"),
                    value: place,
                    "data-step": "step-" + prefix
                }).appendTo("#contributor-questionnaire");
            }
        }

        if ($("#" + previous + "-date").prop("checked")) {
            var previousDate = $("#" + previous + "-from-date").val();
            if (previousDate) {
                var earliest = dayAfter(previousDate);
                var $currentDate = $("#" + prefix + "-from-date");
                lockChecked($("#" + prefix + "-date"));
                showLockedPanel("#" + prefix + "-date-panel");
                $currentDate.attr("min", earliest);
                if ($currentDate.val() && $currentDate.val() < earliest) {
                    $currentDate.val("");
                }
                var $hint = $("#" + prefix + "-date-panel .q-date-hint");
                if (!$hint.length) {
                    $hint = $("<p class='q-date-hint' hidden></p>").appendTo("#" + prefix + "-date-panel");
                }
                $hint.text("Only after " + formatIsoDate(previousDate) + ".").prop("hidden", false);
            }
        }
    }

    function resetStep(prefix) {
        releaseStep(prefix);
        var $step = $("#step-" + prefix);
        $step.find("input[type=checkbox]").prop("checked", false);
        $("#" + prefix + "-from-date").val("");
        $("#" + prefix + "-place-select").val("");
        ["purpose", "date", "place"].forEach(function (kind) {
            var $panel = $("#" + prefix + "-" + kind + "-panel");
            $panel.stop(true, true);
            clearPanelMotion($panel);
            $panel.prop("hidden", true);
        });
    }

    function missingAnswers(prefix) {
        var missing = [];
        if ($("#" + prefix + "-purpose").prop("checked") && $("#" + prefix + "-purpose-panel input:checked").length === 0) {
            missing.push("Select at least one purpose.");
        }
        if ($("#" + prefix + "-date").prop("checked") && !$("#" + prefix + "-from-date").val()) {
            missing.push("Choose a date.");
        }
        if ($("#" + prefix + "-place").prop("checked") && !$("#" + prefix + "-place-select").val()) {
            missing.push("Select a place.");
        }
        return missing;
    }

    function showStepError(prefix, missing) {
        var $nav = $("#" + prefix + "-next").closest(".q-nav");
        var $error = $nav.children(".q-step-error");
        if (!$error.length) {
            $error = $("<p class='q-step-error' role='alert' hidden></p>");
            $nav.prepend($error);
        }
        $error.empty();
        if (!missing.length) {
            $error.prop("hidden", true);
            return;
        }
        missing.forEach(function (text) {
            $error.append($("<span></span>").text(text));
        });
        $error.prop("hidden", false);
    }

    /* Next on the four action questions. Pass the following prefix, or null when it does not exist yet. */
    function bindActionNext(prefix, nextPrefix) {
        $("#" + prefix + "-next").on("click", function () {
            var missing = missingAnswers(prefix);
            showStepError(prefix, missing);
            if (missing.length || !nextPrefix) {
                return;
            }
            syncFromPrevious(nextPrefix);
            fadeSwap($("#step-" + prefix), $("#step-" + nextPrefix), function () {
                $("#" + nextPrefix + "-title").trigger("focus");
            });
        });
    }

    function resetFollowing(prefix) {
        var index = ACTION_STEPS.indexOf(prefix);
        if (index < 0) {
            return;
        }
        for (var i = index + 1; i < ACTION_STEPS.length; i += 1) {
            resetStep(ACTION_STEPS[i]);
        }
    }

    var PANEL_MS = 320;

    function clearPanelMotion($panel) {
        $panel.css({
            height: "",
            paddingTop: "",
            paddingBottom: "",
            marginTop: "",
            marginBottom: "",
            overflow: "",
            opacity: ""
        });
    }

    function openBox($panel) {
        $panel.css({
            height: "auto",
            paddingTop: "",
            paddingBottom: "",
            marginTop: "",
            marginBottom: "",
            overflow: "visible"
        });
        var cs = window.getComputedStyle($panel[0]);
        return {
            height: cs.height,
            paddingTop: cs.paddingTop,
            paddingBottom: cs.paddingBottom,
            marginTop: cs.marginTop,
            marginBottom: cs.marginBottom,
            opacity: 1
        };
    }

    function currentBox($panel) {
        var cs = window.getComputedStyle($panel[0]);
        return {
            height: cs.height,
            paddingTop: cs.paddingTop,
            paddingBottom: cs.paddingBottom,
            marginTop: cs.marginTop,
            marginBottom: cs.marginBottom,
            opacity: parseFloat(cs.opacity)
        };
    }

    /* Fade the submenu and slide the following text with it. Shared by every question. */
    function showPanel(panel, visible, onHidden) {
        var $panel = $(panel);
        $panel.stop(true);

        if (visible) {
            var wasHidden = $panel.prop("hidden");
            var start;
            if (wasHidden) {
                $panel.prop("hidden", false);
                start = {
                    height: "0px",
                    paddingTop: "0px",
                    paddingBottom: "0px",
                    marginTop: "0px",
                    marginBottom: "0px",
                    opacity: 0
                };
            } else {
                start = currentBox($panel);
            }
            var end = openBox($panel);
            $panel.css($.extend({ overflow: "hidden" }, start));
            $panel.animate(end, PANEL_MS, function () {
                clearPanelMotion($panel);
            });
            return;
        }

        if ($panel.prop("hidden")) {
            if (onHidden) {
                onHidden();
            }
            return;
        }

        $panel.css($.extend({ overflow: "hidden" }, currentBox($panel)));
        $panel.animate({
            height: 0,
            paddingTop: 0,
            paddingBottom: 0,
            marginTop: 0,
            marginBottom: 0,
            opacity: 0
        }, PANEL_MS, function () {
            clearPanelMotion($panel);
            $panel.prop("hidden", true);
            if (onHidden) {
                onHidden();
            }
        });
    }

    /* Fade out one screen, then fade in the next. Same page, any later question step.
       Driven with jQuery so it still runs when the OS asks the browser to reduce motion. */
    function fadeSwap($from, $to, onShown) {
        if ($from.data("fading")) {
            return;
        }
        $from.data("fading", true);
        $from.stop(true).animate({ opacity: 0 }, 450, function () {
            $from.css("opacity", "").prop("hidden", true).removeData("fading");
            $to.stop(true).css("opacity", 0).prop("hidden", false);
            if (onShown) {
                onShown();
            }
            $to.animate({ opacity: 1 }, 450, function () {
                $to.css("opacity", "");
            });
        });
    }

    $(function () {
        bindStep("access");
        bindStep("reproduce");

        $("#start-questionnaire").on("click", function () {
            fadeSwap($("#contributor-intro"), $("#contributor-questionnaire"), function () {
                $("#access-title").trigger("focus");
            });
        });

        $("#access-back").on("click", function () {
            fadeSwap($("#contributor-questionnaire"), $("#contributor-intro"), function () {
                $("#start-questionnaire").trigger("focus");
            });
        });

        bindActionNext("access", "reproduce");
        bindActionNext("reproduce", null);

        $("#reproduce-back").on("click", function () {
            fadeSwap($("#step-reproduce"), $("#step-access"), function () {
                $("#access-title").trigger("focus");
            });
        });

        $("#contributor-questionnaire").on("submit", function (event) {
            event.preventDefault();
        });
    });
}(jQuery));
