## Additional Lens Capabilities

Lens has a lot of capabilities built-in to it. This project is not intended to cover every capability with a simple to use yaml interface -- instead we offer key capabilities via a simplified interface while allowing ultimate customization via custom json.

## Adding a new Lens Capability

The way we add capabilities in this project is by first creating new samples in the samples directory containing the feature we want to add.

Once the sample is added, we decide on a config for that feature. Each sample has a corresponding config in configs. 

If the config requires new keys, we update yaml-reference.md at the root of the project to include the new sample.

Otherwise, we use the config and the sample in our tests to ensure that ultimately we are always generating exactly the same json that Kibana / Lens would generate. For each test, we record the "diff" as a snapshot which is the difference between the generated model and the original model from kibana.