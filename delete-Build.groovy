// Récupère le job spécifique
def job = Jenkins.instance.getItemByFullName('unibank.service.testing')

if (job == null) {
    println("Le job 'unibank.service.testing' n'existe pas.")
} else {
    // Supprime tous les builds du job
    job.builds.each { build ->
        build.delete()
    }
    println("Tous les builds du job '${job.fullName}' ont été supprimés.")
}
