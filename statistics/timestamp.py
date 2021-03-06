import os



import matplotlib.pyplot as plt

# set the style for plots
plt.style.use('seaborn-white')
plt.rc({'fontname', 'Ubuntu'})



from network_motifs.data_structures.trace import GetUniqueFunctions
from network_motifs.utilities.constants import human_readable, request_types_per_dataset



def VisualizeDistribution(dataset, distribution, title, filename):
    """
    Use matplotlib to plot the distribution for this dataset and save to
    a distribution folder.
    @params dataset: dataset from which the distribution comes
    @params distribution: the actual distribution to plot
    @params title: the title of the matplotlib figure
    @params filename: the filename sans directory to save this distribution
    """
    # create the output directory if it doesn't exist
    if not os.path.exists('distributions'):
        os.mkdir('distributions')
    if not os.path.exists('distributions/{}'.format(dataset)):
        os.mkdir('distributions/{}'.format(dataset))

    # determine the appropriate units for this distribution
    max_duration = max(distribution)
    if max_duration > 10**8:
        units = 'seconds'
        for iv in range(len(distribution)):
            distribution[iv] = distribution[iv] / 10**9
    else:
        units = 'microseconds'

    # plot the figure
    plt.figure(figsize=(6, 4))

    # write the labels for this set of functions
    plt.title(title, pad=20, fontsize=14)
    plt.ylabel('Time ({})'.format(units), fontsize=12)
    plt.xlabel('No. Appearances: {}'.format(len(distribution)), fontsize=12)

    # plot the distribution
    plt.boxplot(distribution)

    plt.tight_layout()

    output_filename = 'distributions/{}/{}'.format(dataset, filename)
    plt.savefig(output_filename)

    # clear and close this figure
    plt.clf()
    plt.close()



def FunctionDistribution(traces):
    """
    Plot function distributions for the dataset given the traces. Traces
    should contain all of the request types.
    @params traces: the actual traces for the dataset to get distributions from
    """
    dataset = traces[0].dataset
    # not implemented for xtrace
    assert (not dataset == 'xtrace')

    trace_functions = GetUniqueFunctions(traces)

    # begin to keep track of the distributions
    timestamp_distributions = {}
    for function in trace_functions:
        timestamp_distributions[function] = []

    for trace in traces:
        # keep track of function entries for this stack
        entries = {}

        # go through all of the nodes
        for node in trace.nodes:
            # skip annotations
            if node.variant == 'Entry':
                # make sure that the entry is not already in the dictionary
                assert (not node.id in entries)
                # record the timestamp for entry
                entries[node.id] = node.timestamp
            elif node.variant == 'Exit':
                # make sure that an entry exists for this exit
                assert (node.id in entries)
                # determine the time from entry to exit in nanoseconds
                duration = node.timestamp - entries[node.id]
                timestamp_distributions[node.function_id].append(duration)

                # remove this entry
                entries.pop(node.id)

    # for each function plot the distribution
    for iv, function in enumerate(trace_functions):
        distribution = timestamp_distributions[function]

        # skip over annotation only functions
        if not len(distribution): continue

        if dataset == 'openstack':
            # make a human readable title from the function
            split_function_name = function.split(':')
            if len(split_function_name) == 2:
                title = function
            else:
                title = '{}:{}\n{}'.format(split_function_name[0], split_function_name[1], split_function_name[2])
        else:
            title = '{} {}'.format(human_readable[dataset], function)

        filename = 'function-{:04d}.png'.format(iv)

        VisualizeDistribution(dataset, distribution, title, filename)



def RequestTypesDistribution(traces):
    """
    Plot request type distributions for the dataset given the traces.
    Traces should contain all of the request types.
    @params traces: the actual traces for the dataset to get distributions from
    """
    dataset = traces[0].dataset
    trace_request_types = request_types_per_dataset[dataset]

    # begin to keep track of the distributions
    timestamp_distributions = {}
    for request_type in trace_request_types:
        timestamp_distributions[request_type] = []

    for trace in traces:
        # get the duration in seconds
        timestamp_distributions[trace.request_type].append(trace.duration)

    # for each request type, plot the distribution
    for request_type in trace_request_types:
        distribution = timestamp_distributions[request_type]

        # skip over annotation only functions
        if not len(distribution): continue

        filename = 'request-type-{}.png'.format(request_type).lower()

        # get the title for this distribution
        title = '{}: {}'.format(human_readable[dataset], request_type)

        # visiaulize the distribution
        VisualizeDistribution(dataset, distribution, title, filename)
