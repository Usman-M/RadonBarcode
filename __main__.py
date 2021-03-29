import pathlib
from PIL import Image
import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def Search_Algorithm(reference, barcodes):
    search_result = []
    shortest_distance = 113
    closest_match = []
    for barcode in barcodes:
        hamming_distance = 0
        if reference[1] != barcode[1]:
            for i in range(len(barcode[2])):
                if reference[2][i] != barcode[2][i]:
                    hamming_distance += 1
        
        if hamming_distance < shortest_distance and reference[1] != barcode[1]:
            shortest_distance = hamming_distance
            closest_match = barcode
        #print(f'Comparing {reference[1]} with {barcode[1]}: Hamming distance: {hamming_distance}')
    result = f'Searching {reference[0]} ({reference[1]}) -> Found {closest_match[0]} ({closest_match[1]}). Hamming Distance: {shortest_distance}'
    
    if reference[0] == closest_match[0]:
        result += "...HIT"
    else:
        result += "...MISS"
    
    print(result)
    return closest_match


def Barcode_Generator(image, Th_P1_offset = 1.2, Th_P2_offset = 1.5, Th_P3_offset = 2.3, Th_P4_offset = 1.7):
    image_45 = image.rotate(45)
    image_90 = image.rotate(90)
    image_135 = image.rotate(135)

    image_array = numpy.array(image)
    image_45_array = numpy.array(image_45)
    image_90_array = numpy.array(image_90)
    image_135_array = numpy.array(image_135)

    P1 = numpy.sum(image_array, 1)
    P2 = numpy.sum(image_45_array, 1)
    P3 = numpy.sum(image_90_array, 1)
    P4 = numpy.sum(image_135_array, 1)

    Th_P1 = numpy.mean(P1, dtype=int) * Th_P1_offset
    Th_P2 = numpy.mean(P2, dtype=int) * Th_P2_offset
    Th_P3 = numpy.mean(P3, dtype=int) * Th_P3_offset
    Th_P4 = numpy.mean(P4, dtype=int) * Th_P4_offset

    C1 = [0 for i in range(len(P1))]
    C2 = [0 for i in range(len(P2))]
    C3 = [0 for i in range(len(P3))]
    C4 = [0 for i in range(len(P4))]

    # Generate C1 Fragment
    for element in range(len(P1)):
        if P1[element] >= Th_P1:
            C1[element] = 1

    # Generate C2 Fragment
    for element in range(len(P2)):
        if P2[element] >= Th_P2:
            C2[element] = 1
    
    # Generate C3 Fragment
    for element in range(len(P3)):
        if P3[element] >= Th_P3:
            C3[element] = 1

    # Generate C4 Fragment
    for element in range(len(P4)):
        if P4[element] >= Th_P4:
            C4[element] = 1

    RBC = C1 + C2 + C3 + C4
    return RBC

def save_result(match_pairs):
    with PdfPages('Results.pdf') as pdf_file:
        for i in range(0, len(match_pairs), 5):
            figure = plt.figure(figsize = (11, 14))
            figure.tight_layout()
            plt.subplots_adjust(hspace = 0.5)
            for pair in match_pairs[i : i + 5]:
                index = match_pairs[i : i + 5].index(pair)
                # plot known image
                figure.add_subplot(5, 2, 2 * index + 1)
                plt.imshow(Image.open(pair[0][1]))
                plt.title(pair[0][1], pad = 15)
                # plot potential match
                figure.add_subplot(5, 2, 2 * index + 2)
                plt.imshow(Image.open(pair[1][1]))

                if pair[2] == True:
                    plt.title(pair[1][1], pad = 15, color = "green")
                else:
                    plt.title(pair[1][1], pad = 15, color = "red")

            pdf_file.savefig()
            plt.close()
       

if __name__ == "__main__":

    barcodes = []
    # iterate through each class 0..9
    for number in range(10):
        # get the base path for the class
        dir = f"./MNIST_DS/{number}/"
        # iterate through each file/folder in the directory
        for image_path in pathlib.Path(dir).iterdir():
            image = Image.open(image_path)
            RBC = Barcode_Generator(image)
            barcodes.append([number, image_path, RBC])

    hits = 0
    misses = 0
    match_pairs = []
    for i in range(100):
        closest_match = Search_Algorithm(barcodes[i], barcodes)
        if barcodes[i][0] == closest_match[0]:
            hits += 1
            match_pairs.append([barcodes[i][0:2], closest_match[0:2], True])
        else:
            misses += 1
            match_pairs.append([barcodes[i][0:2], closest_match[0:2], False])
    print('--------------------------')
    print(f'Retrieval Accuracy: {100 * hits/(hits + misses)} % [{hits} hits & {misses} misses]')
    print('--------------------------')
    print()
    print('Saving results to ./Results.pdf. This may take a while...')
    print()
    save_result(match_pairs)


