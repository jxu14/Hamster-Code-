function gaydar(name) {
	if(name.sexuality == "gay" && name.name == "Nathan" && name.favColor == "rainbow") {
		return true;
	} else {
		return false;
	}
}

let kappa = {
	sexuality: "gay",
	name: "Nathan",
	favColor: "rainbow"
}

console.log(kappa.gaydar);