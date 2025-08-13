#!/usr/bin/env bash


dirs=(
    ./coverage/unit
    ./coverage/integration
    ./coverage/integration_wo_acme
    ./coverage/both
    ./coverage/both_wo_acme
    ./coverage/acme
    ./coverage/auto
)


# delete all coverage reports
rm -rf ./coverage/*.json

# delete dir/merged, dir/combined.coverprofile, dir/filtered.combined.coverprofile, dir/*.coverprofile.txt
for dir in "${dirs[@]}"; do
    rm -rf "$dir/merged" "$dir/combined.coverprofile" "$dir/filtered.combined.coverprofile" "$dir/"*.txt
done

# one by one
for dir in "${dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "Directory $dir does not exist, skipping."
        continue
    fi
    echo "Creating report for $dir"
    ./coverage_cli.py "$dir" -o ./coverage/$(basename "$dir").json
done

# # pair wise
# for ((i = 0; i < ${#dirs[@]}; i++)); do
#     for ((j = 0; j < ${#dirs[@]}; j++)); do
#         if [ "$i" -eq "$j" ]; then
#             continue
#         fi
#         echo "Creating report for ${dirs[i]} and ${dirs[j]}"
#         ./coverage_cli.py "${dirs[i]}" "${dirs[j]}" -o ./coverage/$(basename "${dirs[i]}")_$(basename "${dirs[j]}").json
#     done
# done
