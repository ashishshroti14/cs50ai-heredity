import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }
    # print(probabilities["Harry"]["gene"])

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_genes` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probability = 1
    zero_gene = set()
    no_trait  = set()
    probab = float(1)

    p_mutate = PROBS["mutation"]
    p_not_mutate = 1-PROBS['mutation']

    # print(people, "wef")

    for person in people:
        if person not in one_gene and person not in two_genes:
            zero_gene.add(person)
        if person not in have_trait:
            no_trait.add(person)

    for person in zero_gene:
        p_mother_passes_good_gene, p_father_passes_good_gene, p_mother_passes_bad_gene, p_father_passes_bad_gene = 1,1,1,1 
        my_person = people[person]
        if my_person["mother"] == None:
            probab *= PROBS["gene"][0]

            # trait_present = int(my_person["trait"])

            # if trait_present == 1:
            #     probab *= PROBS["trait"][0][True]

            # if trait_present == 0:
            #     probab *= PROBS["trait"][0][False]


            # probab *=  trait_present


        else:
            mother = my_person["mother"]
            father = my_person["father"]

            if mother in zero_gene:
                p_mother_passes_good_gene = p_not_mutate
                p_mother_passes_bad_gene = p_mutate
                if father in zero_gene:
                    p_father_passes_good_gene = p_not_mutate
                    p_father_passes_bad_gene = p_mutate

                elif father in one_gene:
                    p_father_passes_good_gene = 0.5 * p_not_mutate + 0.5 * p_mutate
                    p_father_passes_bad_gene = 0.5 * p_not_mutate + 0.5 * p_mutate

                elif father in two_genes:
                    p_father_passes_good_gene = p_mutate
                    p_father_passes_bad_gene = p_not_mutate

            elif mother in one_gene:
                p_mother_passes_good_gene = 0.5 * p_not_mutate + 0.5 * p_mutate
                p_mother_passes_bad_gene = 0.5 * p_not_mutate + 0.5 * p_mutate
                if father in zero_gene:
                    p_father_passes_good_gene = p_not_mutate
                    p_father_passes_bad_gene = p_mutate

                elif father in one_gene:
                    p_father_passes_good_gene = 0.5 * p_not_mutate + 0.5 * p_mutate
                    p_father_passes_bad_gene = 0.5 * p_not_mutate + 0.5 * p_mutate

                elif father in two_genes:
                    p_father_passes_good_gene = p_mutate
                    p_father_passes_bad_gene = p_not_mutate
            
            elif mother in two_genes:
                p_mother_passes_good_gene = p_mutate
                p_mother_passes_bad_gene = p_not_mutate
                if father in zero_gene:
                    p_father_passes_good_gene = p_not_mutate
                    p_father_passes_bad_gene = p_mutate

                elif father in one_gene:
                    p_father_passes_good_gene = 0.5 * p_not_mutate + 0.5 * p_mutate
                    p_father_passes_bad_gene = 0.5 * p_not_mutate + 0.5 * p_mutate

                elif father in two_genes:
                    p_father_passes_good_gene = p_mutate
                    p_father_passes_bad_gene = p_not_mutate


            probab *= p_mother_passes_good_gene* p_father_passes_good_gene
        
        if person in have_trait:
            probab *= PROBS["trait"][0][True]
        



        if person in no_trait:
            probab *= PROBS["trait"][0][False]
        
    for person in one_gene:
        p_mother_passes_good_gene, p_father_passes_good_gene, p_mother_passes_bad_gene, p_father_passes_bad_gene = 1,1,1,1 
        my_person = people[person]
        if my_person["mother"] == None:
            probab *= PROBS["gene"][1]
            # trait_present = int(my_person["trait"])

            # if trait_present == 1:
            #     probab *= PROBS["trait"][0][True]

            # if trait_present == 0:
            #     probab *= PROBS["trait"][0][False]
        else:
            mother = my_person["mother"]
            father = my_person["father"]

            if mother in zero_gene:
                p_mother_passes_good_gene = p_not_mutate
                p_mother_passes_bad_gene = p_mutate
                if father in zero_gene:
                    p_father_passes_good_gene = p_not_mutate
                    p_father_passes_bad_gene = p_mutate

                elif father in one_gene:
                    p_father_passes_good_gene = 0.5 * p_not_mutate + 0.5 * p_mutate
                    p_father_passes_bad_gene = 0.5 * p_not_mutate + 0.5 * p_mutate

                elif father in two_genes:
                    p_father_passes_good_gene = p_mutate
                    p_father_passes_bad_gene = p_not_mutate

            elif mother in one_gene:
                p_mother_passes_good_gene = 0.5 * p_not_mutate + 0.5 * p_mutate
                p_mother_passes_bad_gene = 0.5 * p_not_mutate + 0.5 * p_mutate
                if father in zero_gene:
                    p_father_passes_good_gene = p_not_mutate
                    p_father_passes_bad_gene = p_mutate

                elif father in one_gene:
                    p_father_passes_good_gene = 0.5 * p_not_mutate + 0.5 * p_mutate
                    p_father_passes_bad_gene = 0.5 * p_not_mutate + 0.5 * p_mutate

                elif father in two_genes:
                    p_father_passes_good_gene = p_mutate
                    p_father_passes_bad_gene = p_not_mutate
            
            elif mother in two_genes:
                p_mother_passes_good_gene = p_mutate
                p_mother_passes_bad_gene = p_not_mutate
                if father in zero_gene:
                    p_father_passes_good_gene = p_not_mutate
                    p_father_passes_bad_gene = p_mutate

                elif father in one_gene:
                    p_father_passes_good_gene = 0.5 * p_not_mutate + 0.5 * p_mutate
                    p_father_passes_bad_gene = 0.5 * p_not_mutate + 0.5 * p_mutate

                elif father in two_genes:
                    p_father_passes_good_gene = p_mutate
                    p_father_passes_bad_gene = p_not_mutate
            probab *= p_mother_passes_good_gene* p_father_passes_bad_gene + p_mother_passes_bad_gene* p_father_passes_good_gene 

        if person in have_trait:
            probab *= PROBS["trait"][1][True]
        



        if person in no_trait:
            probab *= PROBS["trait"][1][False]

    for person in two_genes:
        p_mother_passes_good_gene, p_father_passes_good_gene, p_mother_passes_bad_gene, p_father_passes_bad_gene = 1,1,1,1 
        my_person = people[person]
        if my_person["mother"] == None:
            probab *= PROBS["gene"][2]
            # trait_present = int(my_person["trait"])

            # if trait_present == 1:
            #     probab *= PROBS["trait"][0][True]

            # if trait_present == 0:
            #     probab *= PROBS["trait"][0][False]
        else:
            mother = my_person["mother"]
            father = my_person["father"]

            if mother in zero_gene:
                p_mother_passes_good_gene = p_not_mutate
                p_mother_passes_bad_gene = p_mutate
                if father in zero_gene:
                    p_father_passes_good_gene = p_not_mutate
                    p_father_passes_bad_gene = p_mutate

                elif father in one_gene:
                    p_father_passes_good_gene = 0.5 * p_not_mutate + 0.5 * p_mutate
                    p_father_passes_bad_gene = 0.5 * p_not_mutate + 0.5 * p_mutate

                elif father in two_genes:
                    p_father_passes_good_gene = p_mutate
                    p_father_passes_bad_gene = p_not_mutate

            elif mother in one_gene:
                p_mother_passes_good_gene = 0.5 * p_not_mutate + 0.5 * p_mutate
                p_mother_passes_bad_gene = 0.5 * p_not_mutate + 0.5 * p_mutate
                if father in zero_gene:
                    p_father_passes_good_gene = p_not_mutate
                    p_father_passes_bad_gene = p_mutate

                elif father in one_gene:
                    p_father_passes_good_gene = 0.5 * p_not_mutate + 0.5 * p_mutate
                    p_father_passes_bad_gene = 0.5 * p_not_mutate + 0.5 * p_mutate

                elif father in two_genes:
                    p_father_passes_good_gene = p_mutate
                    p_father_passes_bad_gene = p_not_mutate
            
            elif mother in two_genes:
                p_mother_passes_good_gene = p_mutate
                p_mother_passes_bad_gene = p_not_mutate
                if father in zero_gene:
                    p_father_passes_good_gene = p_not_mutate
                    p_father_passes_bad_gene = p_mutate

                elif father in one_gene:
                    p_father_passes_good_gene = 0.5 * p_not_mutate + 0.5 * p_mutate
                    p_father_passes_bad_gene = 0.5 * p_not_mutate + 0.5 * p_mutate

                elif father in two_genes:
                    p_father_passes_good_gene = p_mutate
                    p_father_passes_bad_gene = p_not_mutate
            probab *= p_mother_passes_bad_gene* p_father_passes_bad_gene

        if person in have_trait:
            probab *= PROBS["trait"][2][True]
        



        if person in no_trait:
            probab *= PROBS["trait"][2][False]
    
    


    

    return probab
            
                

                

    # raise NotImplementedError


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    # print(probabilities)
    for person in probabilities:
        # print(one_gene, "djalk;")
        if person in one_gene:
            probabilities[person]["gene"][1] +=  p
        elif person in two_genes:
            # print(person["gene"][2])
            probabilities[person]["gene"][2] +=  p
        else:
            probabilities[person]["gene"][0] += p

        if person in have_trait:
            probabilities[person]["trait"][True] +=  p
        elif person not in have_trait:
            probabilities[person]["trait"][False] +=  p



        
    # raise NotImplementedError


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        for data_type in probabilities[person]:
            # print(data_type)
            data_type_sum = 0
            for sub_data_type in probabilities[person][data_type]:
                # print( probabilities[person][data_type][sub_data_type])
                data_type_sum += probabilities[person][data_type][sub_data_type]
            for sub_data_type in probabilities[person][data_type]:
                if data_type_sum != 0:
                    probabilities[person][data_type][sub_data_type] = probabilities[person][data_type][sub_data_type]/data_type_sum
    # raise NotImplementedError


if __name__ == "__main__":
    main()
