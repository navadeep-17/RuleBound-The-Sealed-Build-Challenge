param location string = resourceGroup().location
param environmentName string = 'rulebound-env'
param appName string = 'rulebound-engine'
param containerImage string = 'mcr.microsoft.com/azuredocs/aci-helloworld:latest'
param entraClientId string = ''
param entraTenantId string = tenant().tenantId

resource containerAppEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: environmentName
  location: location
  properties: {}
}

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: appName
  location: location
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
      }
    }
    template: {
      containers: [
        {
          name: appName
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: entraClientId
            }
            {
              name: 'AZURE_TENANT_ID'
              value: entraTenantId
            }
          ]
        }
      ]
    }
  }
}

output appUrl string = containerApp.properties.configuration.ingress.fqdn
