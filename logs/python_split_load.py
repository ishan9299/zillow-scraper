def load_array_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

def chunk_array(array, chunk_size):
    for i in range(0, len(array), chunk_size):
        yield array[i:(i + chunk_size)]

def main():
    counties = load_array_from_file("county_names.txt")

    num = 0
    for chunk in chunk_array(counties, 12):
        file_name = f"../data/txt/county_list_{num}.txt"
        num += 1
        with open(file_name, "w") as file:
            for item in chunk:
                file.write(str(item) + '\n')

if __name__ == "__main__":
    main()
