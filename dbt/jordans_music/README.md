### Jordan's DBT project for music from Soundcloud and Spotify

- By default, the `.profile` file is created in the folder: `~/.dbt/` and dbt looks to run it from there.

  - If you want to change directory of `profiles` or `dbt_project`, you need to use the `--project-dir my_folder_path` or `--profiles-dir my_folder_path` option when executing command

    ```
    dbt run --project-dir my_folder_path --profiles-dir my_folder_path
    ```

  - The `.profile` is put in the `profiles` folder.

    - The dataset here doesn't matter, it acts as a default entry point for BigQuery schema. `dataset` and `schema` are interchangeable.

  - We should create an `dev` project and a `prod` project in BigQuery. BigQuery allows tables to be accessed from different projects.

### Version

- This project is using `dbt 0.21.1`

- The most stable version is now `1.0`:

  - `seed-paths` have replaced `data-paths` in `dbt-project.yml` with a default value of seeds.

  - In newer versions, seeds are under `seed-paths: ["seeds"]`, currently it is under `data-paths: ["data"]`

  - `model-paths` have replaced `source-paths` in `dbt-project.yml`.

  - The packages-install-path was updated from modules-path. Additionally the default value is now `dbt_packages` instead of `dbt_modules`. You may need to update this value in `clean-targets`.

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
    `dbt test`
    `dbt test --select name_of_model`
    `dbt test --select tag:my_model_tag`
    - https://docs.getdbt.com/reference/node-selection/test-selection-examples
