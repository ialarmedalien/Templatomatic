/*
A KBase module: Templatomatic
*/

module Templatomatic {
    typedef structure {
        string name;
        string ref;
    } ReportResults;

    /*
        This example function may look simple and generic, but it does something super cool involving templates and reports. Run it and see!
    */
    funcdef run_Templatomatic(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
