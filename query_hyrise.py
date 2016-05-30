import argparse
import time
import threading

import requests



def query_hyrise(host, port, query):
    return requests.post(url='http://%s:%d/query' % (host, port), data='query=' + query)


def job(host, port, query, num_threads, num_queries):
    for _ in range(num_queries // num_threads):
        answer = query_hyrise(host, port, query)
        #print "answer"
        print(answer.text)


def benchmark(host, port, query_file, num_threads, num_queries):
    print(query_file)
    with open(query_file, 'r') as query_f:
        query = query_f.read()

    start = time.time()
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=job, args=(host, port, query, num_threads, num_queries))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    print(requests.get(url='http://%s:%d/node_info' % (host, port)))
    print("%f queries/s" % (num_queries/(time.time() - start)))
    return num_queries / (time.time() - start)


def main():
    parser = argparse.ArgumentParser(description='Query Hyrise.')
    parser.add_argument('query_file')
    parser.add_argument('--host', default='192.168.31.38', type=str, help='Hyrise instance (IP address)')
    parser.add_argument('--port', default=5000, type=int, help='Hyrise Port')
    parser.add_argument('--threads', default=1, type=int, help='Threads')
    parser.add_argument('--queries', default=1, type=int, help='queries')
    args = parser.parse_args()

    query_file = args.query_file
    host = args.host
    port = args.port
    threads = args.threads
    num_queries = args.queries

    benchmark(host, port, query_file, threads, num_queries)



if __name__ == '__main__':
    main()
