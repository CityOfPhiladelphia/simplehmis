var HUD = HUD || {};


(function($) {
  'use strict';

  HUD.updateOptionDependentFields = function(showSelector, siblingSelector, undefined) {
    // Show the given sibling fieldset if the select input
    // represented by `this` has the given `showSelector`
    // value.
    var $select = $(this);
    showSelector = (showSelector === undefined ? '[value="1"]' : showSelector);
    siblingSelector = siblingSelector || 'fieldset';

    if ($select.find(showSelector).is(':selected')) {
      $select.parents('fieldset').nextAll(siblingSelector).first().show();
    } else {
      $select.parents('fieldset').nextAll(siblingSelector).first().hide();
    }
  };

  /*== Generic Yes/No fields with dependencies ==*/

  HUD.updateYesOptionDependentFields = function() {
    // Show the fieldset following the select box if the
    // selected value is 'Yes'. Takes advantage of the fact
    // that 'Yes' in HUD fields is always coded to 1.
    HUD.updateOptionDependentFields.call(this, '[value="1"]', 'fieldset');
  };

  HUD.initYesOptionFields = function() {
    $('.has-yes-dependency select')
      .each(function(i, field) { HUD.updateYesOptionDependentFields.call(field); })
      .change(HUD.updateYesOptionDependentFields);
  };

  /*== Substance abuse fields ==*/

  HUD.updateSubstanceAbuseField = function() {
    // HUD Field 4.10, Dependent A
    HUD.updateOptionDependentFields.call(this, '[value="1"],[value="2"],[value="3"]');
  };

  HUD.initSubstanceAbuseField = function() {
    $('.fieldset-substance_abuse select')
      .each(function(i, field) { HUD.updateSubstanceAbuseField.call(field); })
      .change(HUD.updateSubstanceAbuseField);
  };

  /*== Length of time on streets fields ==*/

  HUD.updateHomelessInThreeYearsField = function() {
    // HUD Field 3.17, Dependent A
    HUD.updateOptionDependentFields.call(this, '[value="4"]');
  };

  HUD.initHomelessInThreeYearsField = function() {
    $('.fieldset-homeless_in_three_years select')
      .each(function(i, field) { HUD.updateHomelessInThreeYearsField.call(field); })
      .change(HUD.updateHomelessInThreeYearsField);
  };

  HUD.updatePriorResidenceField = function() {
    // HUD Field 3.9, Dependent A
    HUD.updateOptionDependentFields.call(this, '[value="17"]');
  };

  HUD.initPriorResidenceField = function() {
    $('.fieldset-prior_residence select')
      .each(function(i, field) { HUD.updatePriorResidenceField.call(field); })
      .change(HUD.updatePriorResidenceField);
  };

  $(function() {
    var $selector = $('#id_members-0-hoh_relationship');
    $selector
      .find('option[value="1"]')
      .attr('selected', 'selected');

    HUD.initYesOptionFields();
    HUD.initSubstanceAbuseField();
    HUD.initHomelessInThreeYearsField();
    HUD.initPriorResidenceField();
  });

})(django.jQuery);