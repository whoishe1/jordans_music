### Jordan's DBT project for music from Soundcloud and Spotify

- By default, the `.profile` file is created in the folder: `~/.dbt/` and dbt looks to run it from there.

  - If you want to change directory of `profiles` or `dbt_project`, you need to use the `--project-dir my_folder_path` or `--profiles-dir my_folder_path` option when executing command. When specifying the `--project-dir` path, dbt automatically searches for the `dbt_project.yaml` file, likewise when using the `--profiles-dir` path, dbt looks for the `profiles.yaml` file.

    ```
    dbt run --project-dir my_folder_path --profiles-dir my_folder_path
    ```

  - The `.profile` is put in the `profiles` folder.

    - The dataset here doesn't matter, it acts as a default entry point for BigQuery schema. `dataset` and `schema` are interchangeable.

  - We should create an `dev` project and a `prod` project in BigQuery. BigQuery allows tables to be accessed from different projects.

- Consider using [dbt-expectations](https://github.com/calogica/dbt-expectations) when writing more tests besides the basic tests dbt comes with.

### Version

- This project is using `dbt 1.1`

#### Commands

- use the prefix `dbt` with the following commands:

  - `init *name_of_folder*`: Creates the project folder
  - `debug`: Checks the connection with database
  - `deps`: Installs the test dependencies
  - `seed`: Loads the CSV files into staging tables in the database
  - `run`: Runs the transformations and loads the data into the database
    - use the `--select` command to specific which model you want run
      - `dbt run --select path_to_file`
    - use the `tag` command to run models which have a specific tag set in the `dbt_project.yml`
      - `dbt run -m tags:my_tag`
  - `docs generate`: Generates the documentation of the dbt project
  - `docs serve`: Serves the documentation on a webserver
  - `build`: build and test all selected resources (models, seeds, snapshots, tests)
  - `clean` (CLI only): deletes artifacts present in the dbt project
  - `compile`: compiles (but does not run) the models in a project
  - `debug` (CLI only): debugs dbt connections and projects
  - `deps`: downloads dependencies for a project
  - `docs` : generates documentation for a project
  - `init` (CLI only): initializes a new dbt project
  - `list` (CLI only): lists resources defined in a dbt project
  - `parse` (CLI only): parses a project and writes detailed timing info
  - `run`: runs the models in a project
  - `seed`: loads CSV files into the database
  - `snapshot`: executes "snapshot" jobs defined in a project
  - `source`: provides tools for working with source data (including validating that sources are "fresh")
  - `test`: executes tests defined in a project
  - `rpc` (CLI only): runs an RPC server that clients can submit queries to
  - `run-operation`: runs arbitrary maintenance SQL against the database
  - `test` - run tests on each query

    - https://docs.getdbt.com/reference/node-selection/test-selection-examples
    - by default when you run a test, it will touch all parents.
    - In the example below if you were to run this with just `dbt test -s model0` then dbt will first build `model0` and then `model1`. If you want to avoid this relationship then use `dbt test -s model0 --indirect-selection=cautious`, dbt will then not select this test, because not all parents were selected

    ```
        models:
        - name: model0
            columns:
            - name: customer_id
                tests:
                - relationships:
                    to: ref('model1')
                    field: id
    ```
