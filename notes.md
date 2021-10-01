
## Input files:

* are stored in the directory: /data/inputs/
* have file name: {model}_{job_id}.txt

* have the following format:
    * input is a text:
    ```
    {
        "text": "The string containing text to be processed",
        "model": "Example_Model",
        "input_type": "text",
        "id": "assigned job_id"
    }
    ```

    * input is an eaf file:
    ```
    {
        'input_type': 'eaf_file',
        'eaf_data': string containing parsed eaf file,
        'model': model,
        'id': "assigned job_id",
    }
    ```

## Output files:

* are stored in the directory: /data/results/
* have file name: output_inference_json-{job_id}.std.out

* have the following format:
    * a list of tokens, each of which has the format:
    ```
    {
        "input": "input_token",
        "segmentation": 
            [
                "segmentation_1",
                "segmentation_2",
                "segmentation_3,
                ...
            ],
        "preferred_segmentation": "preferred_segm",
        "custom_segmentation": 
            [
                "custom_segmentation_1",
                "custom_segmentation_2",
                "custom_segmentation_3,
                ...
            ],
        "model": "model_name",
        "sentence_id": "the id of the sentence the token belongs to"
    }
    ```