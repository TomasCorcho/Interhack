# Damm Route Optimizer — Backend

Backend prototype for a **vehicle routing and logistics optimization challenge** developed during a hackathon by a three-person team.

The objective of the project was to generate efficient delivery routes for a beer distribution company while taking into account operational constraints such as truck capacity, customer demand, travel times, loading and unloading operations, and route feasibility.

This repository contains the **backend and optimization work I developed during the hackathon**. The frontend and the final integrated version of the project were developed collaboratively by the team and are available in the [complete team repository](https://github.com/Borgesjesk/damm-route-optimizer).

## My Contribution

My work focused on the **design and implementation of the routing algorithms and backend logic**.

In particular, I worked on:

* modelling the delivery network as a weighted graph,
* designing the logic used to group customers into feasible truck routes,
* implementing route-generation and optimization methods,
* evaluating routes according to travel and operational costs,
* integrating truck-capacity constraints,
* working with customer demand and delivery data,
* and generating route information and graph visualizations for the resulting solutions.

The frontend of the final application was developed by another member of the team.

## Problem

The challenge can be viewed as a variant of the **Vehicle Routing Problem (VRP)**.

Given:

* a distribution centre,
* a set of delivery locations,
* travel times between locations,
* customer demand,
* a limited truck capacity,
* and operational constraints,

the objective is to determine how customers should be assigned to trucks and in which order they should be visited.

A naive search through all possible routes rapidly becomes computationally impractical, so the backend uses heuristic algorithms to construct good solutions within the limited development time of a hackathon.

## Optimization Pipeline

The program follows several stages.

### 1. Delivery Network

The delivery locations are represented as a directed weighted graph using **NetworkX**.

Travel-time data are loaded from an Excel matrix and used as edge weights between locations.

Each customer node can also contain information such as:

* demand,
* product inventory,
* unloading time,
* and availability constraints.

## 2. Customer Clustering — Clarke & Wright

Customers are first divided into groups that can be served by individual trucks.

The implementation uses the **Clarke–Wright Savings Algorithm**.

For two customers (i) and (j), the saving associated with joining their routes is computed from the corresponding travel costs:

$$
S(i,j)=c(0,i)+c(j,0)-c(i,j)
$$

where node (0) represents the distribution centre.

Potential route merges are considered in decreasing order of savings while ensuring that the total demand assigned to a truck does not exceed its capacity.

This produces a set of customer clusters, with each cluster representing the deliveries assigned to one truck.

## 3. Route Optimization

After customers have been assigned to trucks, the visiting order inside each cluster is optimized.

The backend uses a **2-Opt based heuristic** to search for improved routes.

Rather than exhaustively examining every possible permutation, candidate routes are iteratively improved by replacing pairs of edges whenever this reduces the route cost.

This allows useful solutions to be obtained quickly even when the number of delivery locations makes exhaustive search unrealistic.

## 4. Pallet and Truck Capacity

The simulation includes a truck-capacity model.

In the current configuration, each truck has a capacity of:

```text
360 basic units
```

corresponding to six pallets of 60 units each.

Customer orders can contain different product types, and the palletizing logic groups the corresponding products into pallets before calculating the final route information.

The resulting loading and unloading times are incorporated into the route evaluation.

## 5. Dynamic Route Cost

The final cost of a route is not based only on the graph edge weights.

The backend also evaluates operational effects such as:

* travel time,
* unloading/loading time,
* blocked delivery intervals,
* and the return to the distribution centre.

A route that violates a time restriction can therefore be treated as infeasible even if its geometric or travel-time distance would otherwise be attractive.

## 6. Output

When the program runs, it prints a summary of the generated logistics plan to the terminal.

For each truck, the output includes information such as:

* assigned customers,
* total demand,
* estimated route duration,
* delivery order,
* pallet composition,
* and loading information.

The program also generates **graph visualizations of the resulting routes**, allowing the solution produced for each truck to be inspected visually.

## Project Structure

The current hackathon version is contained in the `example/` directory:

```text
example/
├── Almazen3.py
├── Calcular_costo.py
├── clarke_wright.py
├── funciones.py
├── main.py
├── matriz_tiempos_25kmh.xlsx
├── paletizador.py
└── ...
```

### Main files

`main.py`
Coordinates the complete simulation: loading the travel-time matrix, constructing the graph, generating customer demand, assigning customers to trucks, optimizing routes, evaluating the final solution and producing the visualizations.

`clarke_wright.py`
Implements the Clarke–Wright Savings Algorithm used to group customers into capacity-constrained truck routes.

`funciones.py`
Contains route-search and optimization utilities, including the 2-Opt based route optimization logic.

`Calcular_costo.py`
Evaluates the effective cost and feasibility of the generated routes, taking travel time and operational constraints into account.

`paletizador.py`
Implements the palletization and loading logic used to construct the truck manifests and estimate unloading operations.

`matriz_tiempos_25kmh.xlsx`
Contains the travel-time data used to construct the weighted delivery graph.

## Technologies

* Python
* NetworkX
* Pandas
* Matplotlib
* Graph algorithms
* Vehicle routing heuristics
* Clarke–Wright Savings Algorithm
* 2-Opt
* Logistics optimization
* Data visualization

## Running the Project

The backend can be executed from the `example` directory.

Install the required Python packages if necessary:

```bash
pip install networkx pandas matplotlib openpyxl
```

Then run:

```bash
python main.py
```

The program will:

1. load the travel-time matrix,
2. construct the delivery network,
3. generate the delivery demand,
4. assign customers to trucks using Clarke–Wright,
5. optimize each truck route,
6. calculate the resulting logistics costs,
7. print a detailed summary to the terminal,
8. and display graph visualizations of the generated routes.

## Hackathon Context

This project was created during a hackathon by a **three-person team**.

The team divided the work between backend optimization and frontend development. This repository preserves the backend version containing my development history and commits.

A separate repository contains the final integrated application, including the frontend:

[Complete team project — damm-route-optimizer](https://github.com/Borgesjesk/damm-route-optimizer)

## Notes

This repository reflects a **hackathon prototype** rather than a production logistics system.

The emphasis was on rapidly developing and testing a functional optimization approach under time constraints. As a result, some implementation decisions prioritize experimentation and demonstrability over production-level architecture.

