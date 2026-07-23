# Sparkly Auto with Config File

Sparkly Auto recommends a blocking configuration for Sparkly. The recommended
configuration can be exported to a JSON file which can be inspected, modified if necessary, and then used to perform the blocking step.

## Installation

First, clone this repository: 
```bash
git clone https://github.com/wi0lono/sparkly.git
```

Next, follow the installation instructions [here](./install-single-machine.md).

The installation process is identical to Sparkly. The only difference is that when installing the Sparkly package, you should install this fork instead of the original repository:

```bash
pip install git+https://github.com/wi0lono/sparkly.git@main
```


## Step 0: Activate Virtual environment
Once you are done with the installation, make sure your virtual environment is active:
```bash
source ~/sparkly-venv/bin/activate
```

Next, navigate to the examples folder of the repository you cloned:
```bash
cd path_where_you_cloned_this_repository
cd examples
```


## Step 1: Generate a recommended configuration

Run the following command:

```bash
python sparkly_auto_generate_config.py \
    --table_a data/abt_buy/table_a.parquet \
    --table_b data/abt_buy/table_b.parquet \
    --output_config recommended_config.json \
    --top_k 2
```

This runs Sparkly's optimization step and writes the recommended configuration
to `recommended_config.json`.

### Options

| Option | Required | Description |
|---|:---:|---|
| `--table_a` | ✓ | Path to table A (CSV or Parquet). |
| `--table_b` | Optional | Path to table B (CSV or Parquet). |
| `--output_config` | ✓ | Path where the generated JSON configuration will be written. |
| `--top_k` | Optional | Number of recommended configurations to generate (default: `1`). |
| `--index_dir` | Optional | Directory where the temporary Lucene index is created. |

## Step 2: (Optional) Edit the configuration

The generated JSON file contains one or more recommended blocking
configurations. If `--top_k > 1`, the configurations are ordered from best to
worst according to Sparkly's optimization process.


Here's the config file generated from Step 1:

```json
[
    {
        "id_col": "_id",
        "concat_fields": {
            "concat_description_name_price": [
                "name",
                "description",
                "price"
            ]
        },
        "spec": {
            "name": [
                "name.3gram",
                "name.standard"
            ]
        },
        "boost_map": []
    },
    {
        "id_col": "_id",
        "concat_fields": {
            "concat_description_name_price": [
                "name",
                "description",
                "price"
            ]
        },
        "spec": {
            "name": [
                "name.3gram",
                "name.standard"
            ],
            "description": [
                "description.standard"
            ]
        },
        "boost_map": []
    }
]
```

**For most users, `spec` is the field you want to pay attention to.** `spec` maps columns in table B to one or more indexed fields (and analyzers) in table A that Sparkly Auto predicts will produce the best blocking performance.

Each configuration contains the following fields:

| Field | Description |
|---|---|
| `id_col` | The unique identifier column in table A. |
| `concat_fields` | Any concatenated fields that Sparkly Auto created while building the index. |
| `spec` | Maps columns in table B to one or more indexed fields (and analyzers) in table A. This is the field users are most likely to modify. |
| `boost_map` | Optional weights for indexed fields. If empty, all queried fields are weighted equally. |

In most cases, the generated configuration can be used without modification.

## Step 3: Apply the configuration

Run:

```bash
python sparkly_auto_apply_config.py \
    --table_a data/abt_buy/table_a.parquet \
    --table_b data/abt_buy/table_b.parquet \
    --gold data/abt_buy/gold.parquet \
    --config recommended_config.json \
    --output_file candidates.parquet
```

This rebuilds the index using the recommended configuration, performs blocking, optionally computes recall if a gold file is provided, and writes the candidate pairs to `candidates.parquet`. If `--top_k > 1` in Step 1, Sparkly uses the first configuration in the JSON file by default.

The output of this step should be the normal blocking output of Sparkly, ending like this if you have gold data:

```
only showing top 20 rows
true_positives : 1096
recall : 0.9990884229717412
```

### Options

| Option | Required | Description |
|---|:---:|---|
| `--table_a` | ✓ | Path to table A. |
| `--table_b` | Optional | Path to table B. |
| `--config` | ✓ | Path to the recommended configuration JSON file. |
| `--output_file` | Optional | Path where candidate pairs will be written as a Parquet file. |
| `--gold` | Optional | Gold file used to compute recall. |
| `--k` | Optional | Maximum number of candidates returned for each row (default: `50`). |
| `--id_col` | Optional | ID column used during blocking (default: `_id`). |
| `--index_dir` | Optional | Directory where the temporary Lucene index is created. |

## Next steps

For more details on the configuration format, modifying the generated JSON, and
using Sparkly Auto in your own code, see the **Sparkly Auto Configuration Guide**.