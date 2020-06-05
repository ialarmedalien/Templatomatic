/*
A KBase module: Templatomatic
*/

module Templatomatic {

    typedef structure {
      string report_type;
      string workspace_name;
      int workspace_id;
    } TemplatomaticInput;

    typedef structure {
      string report_name;
      string report_ref;
    } ReportResults;

    /*
        This example function may look simple and generic, but it does something super cool involving templates and reports. Run it and see!
    */
    funcdef run_Templatomatic(TemplatomaticInput params) returns (ReportResults output) authentication required;

};
