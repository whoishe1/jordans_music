- dbt and cloud composer can have issues due to dependecies, cloud composer installs python packages when you spin it up.  They do not recommend downgrading the packages.  These packages may have issues with version of dbt.

- If you want hack around to use composer here is a specific version where it works:

    - create composer using cli:
        ```
        gcloud composer environments create my_airflow_dbt_example
        --location us-central1
        --image-version composer-1.17.9-airflow-2.1.4
        ```

- requirements.txt
    ```
    dbt-bigquery==0.21.0
    jsonschema==3.1.1
    packaging==20.9
    ```


- For this specific composer version, you are downgrading jsonschema from `3.2.0` to `3.1.1` and packaging from `21.3` to `20.9`.
