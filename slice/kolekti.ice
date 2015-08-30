module Kolekti {

  sequence<string> MetricNames;
  sequence<string> Arguments;
  struct MetricResult {
    string stdout;
    string stderr;
    int    rc;
    float  duration;
  };

  interface MetricProducer {
    MetricNames listMetrics();
    MetricResult getMetric(string name, Arguments args);
  };
};
