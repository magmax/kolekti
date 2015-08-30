module Kolekti {

  sequence<string> MetricOutput;
  sequence<string> Arguments;

  interface MetricProducer {
    MetricOutput listMetrics();
    string getMetric(string name, Arguments args);
  };
};
